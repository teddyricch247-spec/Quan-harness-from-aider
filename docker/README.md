# Aider Docker images

Two images are built from [`Dockerfile`](./Dockerfile):

| Target | Tag | Contents |
|--------|-----|----------|
| `aider` | `paulgauthier/aider` | Core Aider + Playwright. |
| `aider-full` | `paulgauthier/aider-full` | Core + `help`, `browser`, and extra ML deps. |

Both are **non-root** (user `appuser`, UID 1000), run in a Python virtualenv at
`/venv`, and have `AIDER_ANALYTICS=false`. Aider **never runs a model itself** —
it is a client that talks to a model server over HTTP(S). There is no GPU in the
container and no model is bundled, so point it at an external provider:

- A cloud provider (OpenAI, Anthropic, Gemini, …) via its API key, **or**
- a **local / OpenAI-compatible server** (e.g. Ollama, LM Studio, llama.cpp,
  vLLM) reachable from the container over the network.

Credentials and endpoints are supplied **at runtime** (env vars / CLI flags),
never baked into the image.

## Build

```bash
# Core image
docker build -f docker/Dockerfile -t aider:local --target aider .

# Full image (browser / extra ML deps)
docker build -f docker/Dockerfile -t aider-full:local --target aider-full .
```

For reproducible builds, pin the base image by digest (see the comment at the
top of `Dockerfile`) and pass `--no-cache` only when you want a clean rebuild.

## Run

Mount your project directory into `/app` so Aider edits the real files and the
`~/.aider` cache persists on the host:

```bash
# With a cloud provider
docker run --rm -it \
  -v "$PWD":/app \
  -v "$HOME/.aider":/home/appuser/.aider \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  aider:local --model gpt-4o

# With a local / OpenAI-compatible server (no API key required)
docker run --rm -it \
  -v "$PWD":/app \
  -v "$HOME/.aider":/home/appuser/.aider \
  --network host \
  aider:local \
  --model openai/gpt-4o \
  --openai-api-base http://localhost:11434/v1
```

Notes:
- `--network host` lets the container reach a server on `localhost`. On macOS/Windows
  use `--add-host=host.docker.internal:host-gateway` and point the base URL at
  `http://host.docker.internal:11434/v1` instead.
- `AIDER_ANALYTICS=false` is already set in the image; override only if desired.
- `OPENAI_API_KEY` can be omitted for local servers that don't require auth.

## Health / smoke

```bash
docker run --rm aider:local --help
docker run --rm aider:local --version
```

The image ships a `HEALTHCHECK` (`import aider`) that passes as long as the
Python environment is intact. Inspect the running container with
`docker ps` / `docker inspect`.

## Inspect for secrets

Before publishing, confirm no credentials leaked into the image:

```bash
docker run --rm aider:local printenv | grep -iE 'key|token|secret' || true
docker history --no-trunc aider:local
```

The build relies on `.dockerignore` to exclude `.env`, `.refact`, local
virtualenvs, and the `aider-work/` test checkout.

## Reproducible faculty-demo deployment

A single, repeatable command students can run after cloning the repo:

```bash
# 1. Build the pinned core image
docker build -f docker/Dockerfile -t aider:demo --target aider .

# 2. Launch a disposable, port-mapped session against Ollama on the host
docker run --rm -it \
  -v "$PWD":/app \
  -v "$HOME/.aider":/home/appuser/.aider \
  --add-host=host.docker.internal:host-gateway \
  -e AIDER_ANALYTICS=false \
  aider:demo \
  --model openai/qwen2.5-coder:7b \
  --openai-api-base http://host.docker.internal:11434/v1
```

Swap the model/endpoint for any cloud provider by exporting the matching API key
and changing `--model` / `--openai-api-base`. No code changes are required to
point Aider at a different backend — it is configuration, not a rebuild.
