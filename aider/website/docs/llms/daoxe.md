---
parent: Connecting to LLMs
nav_order: 500
---

# DaoXE

Aider can connect to [DaoXE](https://daoxe.com), a multi-model multi-protocol AI
API gateway for developers. DaoXE exposes an OpenAI-compatible Chat Completions
endpoint at `https://daoxe.com/v1`, and also supports OpenAI Responses and
Anthropic Messages endpoints outside aider's OpenAI-compatible path.

You'll need a DaoXE API key from your [DaoXE account](https://daoxe.com).

> DaoXE is **not available in mainland China**.

First, install aider:

{% include install.md %}

Then configure your API key and endpoint:

```
# Mac/Linux:
export OPENAI_API_BASE=https://daoxe.com/v1
export OPENAI_API_KEY=<key>

# Windows:
setx OPENAI_API_BASE https://daoxe.com/v1
setx OPENAI_API_KEY <key>
# ... restart shell after setx commands
```

Start working with aider and DaoXE on your codebase:

```bash
# Change directory into your codebase
cd /to/your/project

# Use an exact model ID currently available to your DaoXE account
aider --model openai/<model-id>
```

Choose the model ID from your DaoXE account catalog or the public
[models and pricing page](https://daoxe.com/pricing). Account availability can
vary, so prefer the model list returned for your key.

Public setup examples and a low-cost smoke/compare benchmark:
[DaoXE-AI](https://github.com/seven7763/DaoXE-AI).

See the [model warnings](warnings.html)
section for information on warnings which will occur
when working with models that aider is not familiar with.
