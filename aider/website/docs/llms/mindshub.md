---
parent: Connecting to LLMs
nav_order: 500
---

# MindsHub

[MindsHub](https://mindshub.ai) is an OpenAI-compatible inference gateway that
gives you one API key and one bill for many models from different providers
(Claude, GPT, Kimi, DeepSeek and others), all served through a standard
OpenAI chat completions endpoint. Since aider can talk to any
[OpenAI compatible API](openai-compat.md), it works with MindsHub without any
code changes. See the
[MindsHub inference docs](https://docs.mindshub.ai/inference/) for full API
details.

You'll need a [MindsHub API key](https://console.mindshub.ai).

First, install aider:

{% include install.md %}

Then configure your API key and endpoint:

```
# Mac/Linux:
export OPENAI_API_KEY=<your MindsHub API key>
export OPENAI_API_BASE=https://api.mindshub.ai/v1

# Windows:
setx OPENAI_API_KEY <your MindsHub API key>
setx OPENAI_API_BASE https://api.mindshub.ai/v1
# ... restart shell after setx commands
```

Start working with aider and MindsHub on your codebase. Prefix the model
name with `openai/` and use one of the aliases from the
[MindsHub model catalog](https://docs.mindshub.ai/inference/models):

```bash
# Change directory into your codebase
cd /to/your/project

aider --model openai/sonnet     # Claude Sonnet 5
aider --model openai/opus       # Claude Opus 5
aider --model openai/gpt-codex  # GPT 5.3 Codex
aider --model openai/kimi       # Kimi K3
aider --model openai/deepseek   # DeepSeek V4-Pro
```

The full, current list of aliases is returned by MindsHub's models endpoint
and documented at
[docs.mindshub.ai/inference/models](https://docs.mindshub.ai/inference/models).
Aliases track the newest version of a model family, so you don't need to
update your `--model` argument when MindsHub upgrades the underlying model.

Note: send the bare alias to MindsHub, without a vendor prefix, e.g.
`sonnet` rather than `claude-sonnet-5`. Aider itself is the thing that gets
the `openai/` prefix, since that's what tells aider/litellm to talk to your
custom `OPENAI_API_BASE` using the OpenAI protocol.

## Optional: pin settings with `.aider.model.settings.yml`

If you always use the same MindsHub model, you can set it as the default and
pin any extra parameters in a
[`.aider.model.settings.yml`](https://aider.chat/docs/config/adv-model-settings.html#model-settings)
file in your home directory or the root of your git project:

```yaml
- name: openai/sonnet
  extra_params:
    max_tokens: 8192
```

See the [model warnings](warnings.html) page for information on the warnings
aider shows for models it isn't already familiar with; MindsHub's aliases are
not in aider's built-in model metadata, so this warning is expected and can
be ignored.
