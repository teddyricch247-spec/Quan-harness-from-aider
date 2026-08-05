---
parent: Connecting to LLMs
nav_order: 500
---

# QVAC

Aider can connect to local models served by [QVAC](https://qvac.tether.io), an
open-source runtime for local-first, peer-to-peer AI. QVAC exposes an
OpenAI-compatible HTTP server, so aider talks to it like any other
[OpenAI compatible API](/docs/llms/openai-compat.html).

First, install aider:

{% include install.md %}

Then install the QVAC CLI and start the OpenAI-compatible server:

```bash
# Install the CLI
npm i -g @qvac/cli

# Start the OpenAI-compatible server (default port 11434)
qvac serve openai
```

QVAC loads models by alias. Define the aliases you want to serve in a
`qvac.config.json`:

```json
{
  "serve": {
    "models": {
      "gpt-oss-20b": {
        "model": "GPT_OSS_20B_INST_Q4_K_M",
        "preload": true,
        "config": { "ctx_size": 32768 }
      }
    }
  }
}
```

Then configure your API key and endpoint:

```bash
# qvac serve doesn't validate the key, but a non-empty value must be sent
export OPENAI_API_KEY=qvac # Mac/Linux
setx   OPENAI_API_KEY qvac # Windows, restart shell after setx

export OPENAI_API_BASE=http://127.0.0.1:11434/v1 # Mac/Linux
setx   OPENAI_API_BASE http://127.0.0.1:11434/v1 # Windows, restart shell after setx
```

Start working with aider and QVAC on your codebase. Prefix the model name with
`openai/` and use the alias from your `qvac.config.json`:

```bash
# Change directory into your codebase
cd /to/your/project

aider --model openai/gpt-oss-20b
```

See the [model warnings](warnings.html)
section for information on warnings which will occur
when working with models that aider is not familiar with.

## Setting the context window size

QVAC's LLM `ctx_size` defaults to 1024 tokens, which is far too small for
working with aider. Set it explicitly in your `qvac.config.json` (the example
above uses `32768`) so requests aren't truncated.

## Reasoning models

For reasoning-tuned models such as Qwen3.5, set `reasoning_budget: 0` in the
model's `config` to disable the thinking budget, which otherwise interferes
with aider's code edits.

## Use a capable model

Local tool-calling and edit quality are bounded by the model you run. For the
best results with aider, serve a larger capable model such as `gpt-oss-20b`.
