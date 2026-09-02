---
parent: Connecting to LLMs
nav_order: 500
---

# OpenZoo

Aider can connect to [OpenZoo](https://openzoo.fun), an OpenAI compatible
provider with no signup: any API key value is accepted, and usage is paid
per request (by card, or via the x402 protocol from a local burner wallet).

First, install aider:

{% include install.md %}

Then start OpenZoo locally and configure your endpoint:

```
npx openzoo   # serves http://localhost:8402/v1

# Mac/Linux:
export OPENAI_API_BASE=http://localhost:8402/v1
export OPENAI_API_KEY=sk-openzoo

# Windows:
setx OPENAI_API_BASE http://localhost:8402/v1
setx OPENAI_API_KEY sk-openzoo
# ... restart shell after setx commands
```

A hosted endpoint is also available at `https://api.openzoo.fun/v1`.

Start working with aider and OpenZoo on your codebase:

```bash
# Change directory into your codebase
cd /to/your/project

# Prefix the model name with openai/
aider --model openai/z-ai/glm-5.3-flash
```

The free model list at `http://localhost:8402/v1/models` shows every
available model id with live pricing.

See the [model warnings](warnings.html)
section for information on warnings which will occur
when working with models that aider is not familiar with.
