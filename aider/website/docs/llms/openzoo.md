---
parent: Connecting to LLMs
nav_order: 500
---

# OpenZoo

Aider can connect to [OpenZoo](https://openzoo.fun), an OpenAI compatible
provider with no account: a small local proxy (`npx openzoo`) pays for each
request via the x402 protocol from a local burner wallet, and aider talks to
the proxy like any other OpenAI compatible endpoint.

First, install aider:

{% include install.md %}

Then start the OpenZoo proxy and point aider at it:

```
npx openzoo   # serves http://localhost:8402/v1

# Mac/Linux:
export OPENAI_API_BASE=http://localhost:8402/v1
export OPENAI_API_KEY=sk-openzoo   # the proxy ignores the key; any non-empty value

# Windows:
setx OPENAI_API_BASE http://localhost:8402/v1
setx OPENAI_API_KEY sk-openzoo
# ... restart shell after setx commands
```

`npx openzoo address` prints the proxy's wallet — fund it with USDC on Solana
or Base; `npx openzoo balance` shows what is left.

Start working with aider and OpenZoo on your codebase:

```bash
# Change directory into your codebase
cd /to/your/project

# Prefix the model name with openai/
aider --model openai/auto
```

`auto` lets the proxy pick a model per request; the free model list at
`http://localhost:8402/v1/models` shows every available model id (bare names
like `claude-sonnet-5` or `gpt-4o-mini`) with live pricing.

The hosted endpoint `https://api.openzoo.fun/v1` answers HTTP 402 unless the
caller pays x402 or presents an OpenZoo subscription key (`ozk_live_…`);
aider cannot pay x402 itself, so use the local proxy.

See the [model warnings](warnings.html)
section for information on warnings which will occur
when working with models that aider is not familiar with.
