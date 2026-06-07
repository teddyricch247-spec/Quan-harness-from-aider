---
parent: Connecting to LLMs
nav_order: 500
---

# ForAI

Aider can connect to models served through
[ForAI](https://www.forai.ai), an OpenAI-compatible AI gateway
designed for AI agents and developers.

First, install aider:

{% include install.md %}

## Get an API key

Create a ForAI account and get an API key from
[forai.ai](https://www.forai.ai).

## Configure your environment

Set your ForAI API key and OpenAI-compatible API endpoint:

```
# Mac/Linux:
export OPENAI_API_KEY=<your-forai-key>
export OPENAI_API_BASE=https://www.forai.ai/v1

# Windows:
setx OPENAI_API_KEY <your-forai-key>
setx OPENAI_API_BASE https://www.forai.ai/v1
# ... restart shell after setx commands
```

## Run aider

Start working with aider and ForAI on your codebase:

```bash
# Change directory into your codebase
cd /to/your/project

# Prefix the model name with openai/
aider --model openai/gpt-5.5

# Or pass the API settings explicitly
aider \
  --model openai/gpt-5.5 \
  --openai-api-key $OPENAI_API_KEY \
  --openai-api-base https://www.forai.ai/v1
```

## Supported models

ForAI provides access to models including:

- Claude Opus 4.8
- GPT-5.5
- Gemini 3 Flash
- DeepSeek V4
- Qwen 3.8 Max

## Benefits

- OpenAI-compatible API
- Unified billing
- AI-agent optimized
- Multi-provider routing
- Reduced token costs

## Links

- [ForAI](https://www.forai.ai)
- [ForAI docs](https://docs.forai.ai)
