---
meta:
  title: Deploy with SGLang
  description: Serve Muse Glimmer with SGLang for high-throughput local inference with an OpenAI-compatible endpoint.
  keywords: muse glimmer, sglang, deployment, serving, inference
cms:
  alias: /model-api/docs/muse-glimmer/sglang
  target: aidmc
---

# Deploy with SGLang

Serve Muse Glimmer with [SGLang](https://docs.sglang.io) for high-throughput inference behind an OpenAI-compatible endpoint.

## Install {#install}

Muse Glimmer support lives on the `muse-glimmer` branch ([PR #34262](https://github.com/sgl-project/sglang/pull/34262)) rather than in a released version, so install from source:

```bash title="bash"
pip install --upgrade pip
pip install uv
git clone -b muse-glimmer https://github.com/sgl-project/sglang.git
cd sglang
uv pip install -e "python[all]"
```

A prebuilt image is the alternative:

```bash title="bash"
docker pull lmsysorg/sglang:dev-muse-glimmer
```

## Start the server {#start-the-server}

Serve the BF16 checkpoint:

```bash title="bash"
sglang serve \
  --model-path meta-models/Muse-Glimmer-30B \
  --served-model-name muse-glimmer \
  --reasoning-parser muse \
  --tool-call-parser muse \
  --mem-fraction-static 0.85 \
  --host 0.0.0.0 --port 30000
```

`--reasoning-parser muse` splits the thinking channel into `message.reasoning_content`, and `--tool-call-parser muse` emits structured `message.tool_calls`. SGLang's parser name for both flags is `muse`. Pass both flags explicitly.

`--served-model-name muse-glimmer` sets the name the API answers to. Without it, SGLang serves under the full `--model-path` value and the requests below won't match.

Lower `--mem-fraction-static` if the server runs out of memory during startup.

For the GGUF, NVFP4, and Apple silicon MLX checkpoints, and for the hardware SGLang has verified each one on, see the [official guide](https://docs.sglang.io/cookbook/autoregressive/Meta/MuseGlimmer).

## Verify the server {#verify}

SGLang exposes an OpenAI-compatible endpoint on port 30000:

```bash title="curl"
curl http://localhost:30000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "muse-glimmer",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "max_tokens": 512
  }'
```

Reasoning comes back under `message.reasoning_content`, and tool calls arrive as a standard `tool_calls` array. Parsing happens server-side, so an OpenAI-compatible harness needs no [ATEM](/docs/muse-glimmer/prompting#tool-calling)-specific handling.

## Stop tokens {#stop-tokens}

Muse Glimmer needs `eos_token_id = [<|end_of_text|>, <|eot|>]`. Never stop on `<|eom|>`, which ends a message while the turn continues. See [special tokens](/docs/muse-glimmer/prompting#special-tokens).

There's no serve flag for this. SGLang builds its stop set at load time by unioning `eos_token_id` from the checkpoint's `config.json` and its `generation_config.json`, so the checkpoint metadata is where you set it. Because it's a union, a request can add IDs through `stop_token_ids` but can't remove them.

## Next steps

- Speed up generation with [DFlash speculative decoding](/docs/muse-glimmer/spec-decode).
- Compare runtimes on [Run inference](/docs/muse-glimmer/deploy).
- Tune prompts and reasoning with the [prompting guide](/docs/muse-glimmer/prompting).
