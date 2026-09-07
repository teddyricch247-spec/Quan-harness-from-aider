---
parent: Connecting to LLMs
nav_order: 510
---

# Standard Compute

You can use [Standard Compute](https://standardcompute.com/) with aider
through its OpenAI-compatible API. Its `standardcompute` model routes
requests across models and providers, so you can keep using aider without
manually switching between provider accounts.

You need a [Standard Compute API key](https://standardcompute.com/dashboard).

First, install aider:

{% include install.md %}

Set the endpoint and your API key in the shell where you run aider:

```bash
# Mac/Linux
export OPENAI_API_BASE=https://api.stdcmpt.com/v1
export OPENAI_API_KEY="your-standard-compute-api-key"
```

```powershell
# Windows PowerShell (current session)
$env:OPENAI_API_BASE = "https://api.stdcmpt.com/v1"
$env:OPENAI_API_KEY = "<your-standard-compute-api-key>"
```

Start aider in your project:

```bash
aider --model openai/standardcompute
```

Keep the `openai/` prefix: it selects aider's OpenAI-compatible connection.
The model sent to Standard Compute is `standardcompute`, a routing alias,
rather than the name of a pinned upstream model.

If aider reports unknown model metadata, see
[model warnings](warnings.html) and
[advanced model settings](../config/adv-model-settings.html).
Standard Compute's subscription and usage are billed separately from aider;
see its [current plans](https://standardcompute.com/pricing).
