import unittest

from aider.pricing import ModelPricing


class TestModelPricing(unittest.TestCase):
    def test_known_model(self):
        info = {
            "input_cost_per_token": 3.0 / 1_000_000,
            "output_cost_per_token": 15.0 / 1_000_000,
        }
        pricing = ModelPricing.from_model_info(info)

        self.assertIsNotNone(pricing)
        self.assertAlmostEqual(pricing.input_cost_per_million, 3.0)
        self.assertAlmostEqual(pricing.output_cost_per_million, 15.0)
        self.assertIsNone(pricing.input_cost_per_million_cache_hit)

    def test_known_model_with_cache_hit_price(self):
        info = {
            "input_cost_per_token": 3.0 / 1_000_000,
            "output_cost_per_token": 15.0 / 1_000_000,
            "input_cost_per_token_cache_hit": 0.3 / 1_000_000,
        }
        pricing = ModelPricing.from_model_info(info)

        self.assertIsNotNone(pricing)
        self.assertAlmostEqual(pricing.input_cost_per_million_cache_hit, 0.3)

    def test_unknown_model_no_input_price(self):
        info = {"output_cost_per_token": 15.0 / 1_000_000}
        self.assertIsNone(ModelPricing.from_model_info(info))

    def test_unknown_model_zero_input_price(self):
        info = {
            "input_cost_per_token": 0,
            "output_cost_per_token": 15.0 / 1_000_000,
        }
        self.assertIsNone(ModelPricing.from_model_info(info))

    def test_unknown_model_empty_info(self):
        self.assertIsNone(ModelPricing.from_model_info({}))

    def test_zero_tokens(self):
        pricing = ModelPricing(input_cost_per_million=3.0, output_cost_per_million=15.0)
        self.assertEqual(pricing.estimate_cost(0, 0), 0)

    def test_calculation_correctness(self):
        pricing = ModelPricing(input_cost_per_million=3.0, output_cost_per_million=15.0)
        cost = pricing.estimate_cost(20_000, 3_000)

        expected = 20_000 / 1_000_000 * 3.0 + 3_000 / 1_000_000 * 15.0
        self.assertAlmostEqual(cost, expected)

    def test_calculation_with_cache_write(self):
        pricing = ModelPricing(input_cost_per_million=3.0, output_cost_per_million=15.0)
        cost = pricing.estimate_cost(20_000, 3_000, cache_write_tokens=1_000)

        expected = (
            1_000 / 1_000_000 * 3.0 * 1.25 + 20_000 / 1_000_000 * 3.0 + 3_000 / 1_000_000 * 15.0
        )
        self.assertAlmostEqual(cost, expected)

    def test_calculation_with_cache_hit(self):
        pricing = ModelPricing(input_cost_per_million=3.0, output_cost_per_million=15.0)
        cost = pricing.estimate_cost(20_000, 3_000, cache_hit_tokens=1_000)

        expected = (
            1_000 / 1_000_000 * 3.0 * 0.10 + 20_000 / 1_000_000 * 3.0 + 3_000 / 1_000_000 * 15.0
        )
        self.assertAlmostEqual(cost, expected)

    def test_calculation_with_cache_hit_price(self):
        pricing = ModelPricing(
            input_cost_per_million=3.0,
            output_cost_per_million=15.0,
            input_cost_per_million_cache_hit=0.3,
        )
        cost = pricing.estimate_cost(20_000, 3_000, cache_hit_tokens=1_000)

        expected = (
            0.3 / 1_000_000 * 1_000
            + (20_000 - 0.3 / 1_000_000) / 1_000_000 * 3.0
            + 3_000 / 1_000_000 * 15.0
        )
        self.assertAlmostEqual(cost, expected)

    def test_estimate_cost_matches_previous_compute_costs(self):
        info = {
            "input_cost_per_token": 3.0 / 1_000_000,
            "output_cost_per_token": 15.0 / 1_000_000,
        }
        pricing = ModelPricing.from_model_info(info)

        cost = pricing.estimate_cost(20_000, 3_000, cache_write_tokens=500, cache_hit_tokens=250)

        expected = (
            500 / 1_000_000 * 3.0 * 1.25
            + 250 / 1_000_000 * 3.0 * 0.10
            + 20_000 / 1_000_000 * 3.0
            + 3_000 / 1_000_000 * 15.0
        )
        self.assertAlmostEqual(cost, expected)


if __name__ == "__main__":
    unittest.main()
