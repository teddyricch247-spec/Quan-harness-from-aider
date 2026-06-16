---
parent: Connecting to LLMs
nav_order: 500
---

# OpenPaths

Aider can connect to [models provided by OpenPaths](https://openpaths.io),
an OpenAI-compatible gateway that gives you access to many models through a single API.
You'll need an [OpenPaths API key](https://openpaths.io/account).

First, install aider:

{% include install.md %}

Then configure your API key and endpoint:

```
# Mac/Linux:
export OPENAI_API_BASE=https://openpaths.io/v1
export OPENAI_API_KEY=<key>

# Windows:
setx OPENAI_API_BASE https://openpaths.io/v1
setx OPENAI_API_KEY <key>
# ... restart shell after setx commands
```

Start working with aider and OpenPaths on your codebase:

```bash
# Change directory into your codebase
cd /to/your/project

# Prefix the model name with openai/ to use the OpenAI-compatible path
aider --model openai/openpaths/auto

# Or pick a model better suited to coding
aider --model openai/openpaths/auto-code
```

You can browse the available models at
[https://openpaths.io/v1/models](https://openpaths.io/v1/models).

See the [model warnings](warnings.html)
section for information on warnings which will occur
when working with models that aider is not familiar with.
