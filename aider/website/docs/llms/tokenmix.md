---
parent: Connecting to LLMs
nav_order: 510
---

# TokenMix

Aider can connect to [TokenMix](https://tokenmix.ai/), an OpenAI-compatible API gateway
with 300+ models across 17 vendors — including OpenAI, Anthropic and Google models,
plus Chinese models that are otherwise hard to access from outside China
(Qwen, DeepSeek, Doubao, GLM, Kimi, Hunyuan).

First, install aider:

{% include install.md %}

Then configure your key and endpoint using TokenMix's OpenAI-compatible base URL:

```
export OPENAI_API_BASE=https://api.tokenmix.ai/v1 # Mac/Linux
export OPENAI_API_KEY=<your-tokenmix-key>          # Mac/Linux

setx OPENAI_API_BASE https://api.tokenmix.ai/v1    # Windows, restart shell after setx
setx OPENAI_API_KEY <your-tokenmix-key>            # Windows, restart shell after setx
```

Start working with aider, prefixing model names with `openai/`:

```bash
# Change directory into your codebase
cd /to/your/project

aider --model openai/deepseek/deepseek-v3.2
# or
aider --model openai/qwen/qwen3.7-max
```

See the [model warnings](https://aider.chat/docs/llms/warnings.html) section for working with unfamiliar models.
