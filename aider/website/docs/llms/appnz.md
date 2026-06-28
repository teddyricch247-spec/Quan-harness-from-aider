---
parent: Connecting to LLMs
nav_order: 500
---

# app.nz

Aider can connect to [app.nz](https://app.nz), a hosted OpenAI compatible LLM
gateway. app.nz exposes an auto-router that picks a capable model for each
request, plus task-specific variants.

First, install aider:

{% include install.md %}

Then configure your API key and endpoint:

```
# Mac/Linux:
export OPENAI_API_BASE=https://app.nz/v1
export OPENAI_API_KEY=app_live_...

# Windows:
setx OPENAI_API_BASE https://app.nz/v1
setx OPENAI_API_KEY app_live_...
# ... restart shell after setx commands
```

Start working with aider and app.nz on your codebase:

```bash
# Change directory into your codebase
cd /to/your/project

# Prefix the model name with openai/
aider --model openai/app/auto
```

## Auto-routing and variants

`app/auto` automatically routes each request to a suitable model. You can also
target a specific routing profile:

```bash
# Optimized for code editing
aider --model openai/app/auto-code

# Optimized for reasoning-heavy tasks
aider --model openai/app/auto-reasoning
```

Other variants include `openai/app/auto-fast`, `openai/app/auto-cheap`, and
`openai/app/auto-vision`. See the [app.nz docs](https://app.nz/docs) for the
full list.

See the [model warnings](warnings.html)
section for information on warnings which will occur
when working with models that aider is not familiar with.
