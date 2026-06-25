---
parent: Connecting to LLMs
nav_order: 505
---

# TrustedRouter

Aider can connect to [TrustedRouter](https://trustedrouter.com) through the
OpenAI-compatible API. TrustedRouter provides an open-source and verifiable
attested router with zero prompt and output logging by default. This can be
useful when aider is working with private source code, issue context, or
customer data.

First, install aider:

{% include install.md %}

Then configure your TrustedRouter API key and endpoint:

```
# Mac/Linux:
export OPENAI_API_BASE=https://api.trustedrouter.com/v1
export OPENAI_API_KEY=<your-trustedrouter-api-key>

# Windows:
setx OPENAI_API_BASE https://api.trustedrouter.com/v1
setx OPENAI_API_KEY <your-trustedrouter-api-key>
# ... restart shell after setx commands
```

Start working with aider and TrustedRouter on your codebase:

```bash
# Change directory into your codebase
cd /to/your/project

# Use automatic routing
aider --model openai/trustedrouter/auto

# Prefer zero data retention routes
aider --model openai/trustedrouter/zdr

# Prefer end-to-end encrypted routes where available
aider --model openai/trustedrouter/e2e
```

You can also use a specific model ID exposed by TrustedRouter with the same
`openai/` prefix.

