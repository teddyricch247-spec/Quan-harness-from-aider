---
parent: Connecting to LLMs
nav_order: 500
---

# Opper

Aider can connect to models served by [Opper](https://opper.ai),
an AI gateway that provides 700+ models behind one OpenAI-compatible API
with a single key, with EU or US routing per model route.
You'll need an Opper API key from [platform.opper.ai](https://platform.opper.ai).

First, install aider:

{% include install.md %}

Then configure Opper as an OpenAI compatible endpoint:

```
# Mac/Linux:
export OPENAI_API_BASE=https://api.opper.ai/v3/compat
export OPENAI_API_KEY=<key>

# Windows:
setx OPENAI_API_BASE https://api.opper.ai/v3/compat
setx OPENAI_API_KEY <key>
# ... restart shell after setx commands
```

Start working with aider and Opper on your codebase:

```bash
# Change directory into your codebase
cd /to/your/project

# Opper model ids are <provider>/<model-name>.
# Prefix them with openai/ so aider uses its OpenAI compatible client:
aider --model openai/anthropic/claude-opus-5

aider --model openai/aws/gpt-5.6-sol

aider --model openai/alibaba:global/deepseek-v4-pro
```

The leading `openai/` tells aider to send the request to your
`OPENAI_API_BASE`; the rest of the string, e.g. `anthropic/claude-opus-5`,
is sent to Opper as the model id.

The full list of model ids is served at
`https://api.opper.ai/v3/compat/models` (authenticated with your key).
See [Opper's aider setup page](https://opper.ai/apps/aider) for more details.

See the [model warnings](warnings.html)
section for information on warnings which will occur
when working with models that aider is not familiar with.
