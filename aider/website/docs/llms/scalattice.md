---
parent: Connecting to LLMs
nav_order: 410
---

# Scalattice

Scalattice is an OpenAI-compatible inference marketplace.
Create a key in the [developer dashboard](https://scalattice.cloud/developers).

First, install aider:

{% include install.md %}

Then point aider at Scalattice:

```
# Mac/Linux:
export OPENAI_API_BASE=https://api.scalattice.cloud/v1
export OPENAI_API_KEY=<slt_key>

# Windows:
setx OPENAI_API_BASE https://api.scalattice.cloud/v1
setx OPENAI_API_KEY <slt_key>
# ... restart the shell after setx
```

Start working with aider on your codebase:

```bash
cd /to/your/project

aider --model openai/qwen-3-14b
```

Catalog IDs match `GET https://api.scalattice.cloud/v1/models`.
Useful starting points for code work:

- `openai/qwen-3-coder-30b-a3b`
- `openai/qwen-3-14b`
- `openai/glm-4.7-flash`

If your LiteLLM build already includes the Scalattice provider, you can use
the native prefix instead:

```
export SCALATTICE_API_KEY=<slt_key>
aider --model scalattice/qwen-3-14b
aider --list-models scalattice/
```
