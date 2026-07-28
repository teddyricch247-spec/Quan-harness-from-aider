---
parent: Connecting to LLMs
nav_order: 450
---

# Rapid-MLX

Aider can connect to models served locally by [Rapid-MLX](https://rapidmlx.com), an
Apple-Silicon-native inference server (pure MLX) that exposes an OpenAI-compatible API.

First, install aider:

{% include install.md %}

Install Rapid-MLX and start serving a model (it listens on `http://localhost:8000`):

```bash
# Install with Homebrew (or: pip install rapid-mlx)
brew install rapid-mlx

# Serve a model
rapid-mlx serve qwen3.5-9b-4bit
```

Then point aider at its OpenAI-compatible endpoint:

```bash
# Mac/Linux:
export OPENAI_API_BASE=http://localhost:8000/v1
export OPENAI_API_KEY=rapid-mlx # any placeholder; the local server doesn't authenticate

# Windows:
setx OPENAI_API_BASE http://localhost:8000/v1
setx OPENAI_API_KEY rapid-mlx
# ... restart shell after setx commands
```

```bash
# Change directory into your codebase
cd /to/your/project

# Prefix the model name with openai/
aider --model openai/qwen3.5-9b-4bit
```

Browse the available models by your Mac's RAM at
[models.rapidmlx.com](https://models.rapidmlx.com/). See the
[model warnings](warnings.html) section for information on warnings which will occur
when working with models that aider is not familiar with.
