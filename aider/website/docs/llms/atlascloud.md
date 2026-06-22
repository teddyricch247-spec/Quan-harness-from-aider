---
parent: Connecting to LLMs
nav_order: 500
---

# Atlas Cloud

Aider can connect to [Atlas Cloud](https://www.atlascloud.ai), an OpenAI-compatible
API gateway that provides access to 300+ models through a single endpoint.
You'll need an [Atlas Cloud API key](https://www.atlascloud.ai).

First, install aider:

{% include install.md %}

Then configure your API key and endpoint. Atlas Cloud exposes an OpenAI-compatible
API, so point aider at its base URL:

```
# Mac/Linux:
export OPENAI_API_BASE=https://api.atlascloud.ai/v1
export OPENAI_API_KEY=<your-atlas-cloud-key>

# Windows:
setx OPENAI_API_BASE https://api.atlascloud.ai/v1
setx OPENAI_API_KEY <your-atlas-cloud-key>
# ... restart shell after setx commands
```

Start working with aider and Atlas Cloud on your codebase:

```bash
# Change directory into your codebase
cd /to/your/project

# Prefix the model name with openai/
aider --model openai/<model-name>
```

Since Atlas Cloud is accessed through aider's OpenAI-compatible path, see the
[OpenAI compatible APIs](openai-compat.html) page and the
[model warnings](warnings.html) section for more details about working with
models that aider is not already familiar with.
