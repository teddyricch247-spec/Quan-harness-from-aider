"""Estimate API usage costs from token counts and model pricing.

Costs are estimated from per-million-token prices, the same unit used by
model providers and litellm's model pricing database.
"""


class ModelPricing:
    """Per-million-token prices for a model, in USD."""

    def __init__(
        self, input_cost_per_million, output_cost_per_million, input_cost_per_million_cache_hit=None
    ):
        self.input_cost_per_million = input_cost_per_million
        self.output_cost_per_million = output_cost_per_million
        self.input_cost_per_million_cache_hit = input_cost_per_million_cache_hit

    @classmethod
    def from_model_info(cls, info):
        """Build pricing from a model info dict.

        Model info dicts store prices per token (eg ``input_cost_per_token``).
        Returns None when the input price is missing or zero, so callers
        never guess at unknown pricing.
        """
        input_cost_per_token = info.get("input_cost_per_token")
        if not input_cost_per_token:
            return None

        output_cost_per_token = info.get("output_cost_per_token") or 0

        input_cost_per_token_cache_hit = info.get("input_cost_per_token_cache_hit")
        if input_cost_per_token_cache_hit:
            return cls(
                input_cost_per_million=input_cost_per_token * 1_000_000,
                output_cost_per_million=output_cost_per_token * 1_000_000,
                input_cost_per_million_cache_hit=input_cost_per_token_cache_hit * 1_000_000,
            )

        return cls(
            input_cost_per_million=input_cost_per_token * 1_000_000,
            output_cost_per_million=output_cost_per_token * 1_000_000,
        )

    def estimate_cost(self, input_tokens, output_tokens, cache_write_tokens=0, cache_hit_tokens=0):
        """Estimate the API cost for a request, in USD."""
        cost = 0

        input_cost_per_token = self.input_cost_per_million / 1_000_000
        output_cost_per_token = self.output_cost_per_million / 1_000_000

        if self.input_cost_per_million_cache_hit is not None:
            # deepseek:
            # prompt_cache_hit_tokens + prompt_cache_miss_tokens
            #    == prompt_tokens == total tokens that were sent
            #
            # must be deepseek
            input_cost_per_token_cache_hit = self.input_cost_per_million_cache_hit / 1_000_000
            cost += input_cost_per_token_cache_hit * cache_hit_tokens
            cost += (input_tokens - input_cost_per_token_cache_hit) * input_cost_per_token
        else:
            # Anthropic:
            # cache_creation_input_tokens + cache_read_input_tokens + prompt
            #    == total tokens that were
            #
            # hard code the anthropic adjustments, no-ops for other models
            # since cache_x_tokens == 0
            cost += cache_write_tokens * input_cost_per_token * 1.25
            cost += cache_hit_tokens * input_cost_per_token * 0.10
            cost += input_tokens * input_cost_per_token

        cost += output_tokens * output_cost_per_token
        return cost
