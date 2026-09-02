---
meta:
  title: Deploy with vLLM
  description: Serve Muse Glimmer with vLLM for production-grade throughput and OpenAI-compatible endpoints.
  keywords: muse glimmer, vllm, deployment, serving, inference
cms:
  alias: /model-api/docs/muse-glimmer/vllm
  target: aidmc
---

# Deploy with vLLM

Serve Muse Glimmer with [vLLM](https://docs.vllm.ai/) for high-throughput, low-latency inference with an OpenAI-compatible API endpoint. vLLM handles continuous batching, PagedAttention, and tensor parallelism out of the box.

> [!IMPORTANT] The vLLM recipe is source of truth
> The [official vLLM Muse Glimmer recipe](https://recipes.vllm.ai/meta-models/Muse-Glimmer-30B) is the source of truth for the image tag, flags, and hardware requirements. vLLM moves faster than this page: check the recipe first when a command here doesn't match what you see.

## Prerequisites {#prerequisites}

- Docker with the NVIDIA container runtime
- An NVIDIA GPU with drivers for CUDA 13.0, which is what the image is pinned to
- 72 GB of VRAM to serve, on one card or across several

## Install {#install}

Docker is the supported path:

```bash title="bash"
docker pull vllm/vllm-openai:muse-glimmer
```

`pip install vllm` doesn't serve this model. Muse Glimmer support in vLLM is an open, unmerged pull request ([vllm-project/vllm#51655](https://github.com/vllm-project/vllm/pull/51655)), so the model code and the `muse_glimmer` parsers are absent from every released wheel. The recipe sets `pip: false` for that reason, and the image is how you get the unreleased code.

The image is roughly 10.5 GB and publishes `linux/amd64` and `linux/arm64`. There's no published ROCm image; on ROCm, build from the pull request.

What the image gives you:

| Capability | How you get it |
| --- | --- |
| Text model (`MuseGlimmerForCausalLM`) | Automatic, with no `trust_remote_code` |
| Tool-call parser | `--tool-call-parser muse_glimmer` |
| Reasoning parser | `--reasoning-parser muse_glimmer` |
| Chat template | Ships with the checkpoint as `chat_template.jinja`. Don't pass `--chat-template`. |
| Model config | Automatic (`muse-glimmer`, `muse_glimmer_text`, `muse_glimmer_vision`) |

Parser names use underscores. vLLM matches `muse_glimmer` literally, so the hyphenated spelling fails. `--served-model-name muse-glimmer` is a label you choose, and it stays hyphenated.

## Start the server {#start-the-server}

The image sets `ENTRYPOINT ["vllm", "serve"]`, so everything after the image name is appended to that. Pass the model and flags directly rather than retyping `vllm serve` or calling `python -m vllm.entrypoints.openai.api_server`.

```bash title="bash"
docker run --rm --gpus all --ipc=host \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:muse-glimmer \
  meta-models/Muse-Glimmer-30B \
  --served-model-name muse-glimmer \
  --tensor-parallel-size 1 \
  --enable-auto-tool-choice \
  --tool-call-parser muse_glimmer \
  --reasoning-parser muse_glimmer \
  --generation-config auto
```

The flags from `--served-model-name` down are the recipe's argument list for a single card. The `docker run` wrapper around them is standard vLLM boilerplate, so adjust it to your host. Mounting `~/.cache/huggingface` is what stops the container re-downloading roughly 60 GB of weights on every start.

To serve weights you've already downloaded, mount them and pass the path instead of a Hub id:

```bash title="bash"
docker run --rm --gpus all --ipc=host \
  -p 8000:8000 \
  -v /path/to/Muse-Glimmer-30B:/model \
  vllm/vllm-openai:muse-glimmer \
  /model \
  --served-model-name muse-glimmer \
  --tensor-parallel-size 1 \
  --enable-auto-tool-choice \
  --tool-call-parser muse_glimmer \
  --reasoning-parser muse_glimmer \
  --generation-config auto
```

To serve across multiple GPUs, raise the tensor-parallel size:

```bash title="bash"
docker run --rm --gpus all --ipc=host \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:muse-glimmer \
  meta-models/Muse-Glimmer-30B \
  --served-model-name muse-glimmer \
  --tensor-parallel-size 2 \
  --enable-auto-tool-choice \
  --tool-call-parser muse_glimmer \
  --reasoning-parser muse_glimmer \
  --generation-config auto
```

For tighter memory, at a cost in throughput and context:

```bash title="bash"
docker run --rm --gpus all --ipc=host \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:muse-glimmer \
  meta-models/Muse-Glimmer-30B \
  --served-model-name muse-glimmer \
  --gpu-memory-utilization 0.9 --max-model-len 8300 --enforce-eager \
  --enable-auto-tool-choice \
  --tool-call-parser muse_glimmer \
  --reasoning-parser muse_glimmer \
  --generation-config auto
```

> [!NOTE] Budget 72 GB of VRAM
> That is what the recipe asks for: the bf16 weights are roughly 60 GB, and the rest goes to KV cache, activations, and CUDA overhead. Sizing to the weights alone is the usual way to run out of memory shortly after startup.

The flags that carry Muse Glimmer-specific behavior:

| Flag | Why |
| --- | --- |
| `--served-model-name muse-glimmer` | The name the API answers to. Every example here sends `"model": "muse-glimmer"`. |
| `--enable-auto-tool-choice` | Lets the model decide when to call a tool. |
| `--tool-call-parser muse_glimmer` | Converts native ATEM output into standard OpenAI `tool_calls`. |
| `--reasoning-parser muse_glimmer` | Routes the thinking channel to `message.reasoning` instead of leaking it into content. |
| `--generation-config auto` | Picks up the checkpoint's published sampling settings and stop tokens. |
| `--tensor-parallel-size N` | Number of GPUs for tensor parallelism. |
| `--max-model-len N` | Caps the sequence length to limit KV-cache memory. |

> [!NOTE] Stream reasoning workloads
> Muse Glimmer is a reasoning model that produces long chain-of-thought. Request streaming (`"stream": true`) for reasoning workloads so long generations don't hit request timeouts, and give `max_tokens` enough headroom for the reasoning trace plus the final answer.

## Sampling {#sampling}

Serve with `--generation-config auto`, as every command above does, and vLLM picks up the checkpoint's published sampling settings: temperature 1.0, top_p 0.95, and top_k 64.

> [!WARNING] Don't run greedy
> Don't run this model greedy. Sending `"temperature": 0` overrides the published settings, and the recipe advises against it. If you set sampling per request, carry all three values rather than a bare temperature.

## Send a request {#send-a-request}

The server exposes an OpenAI-compatible chat completions endpoint:

```bash title="curl"
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "muse-glimmer",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Write a Python function to compute Fibonacci numbers."}
    ],
    "max_tokens": 2048,
    "stream": true
  }'
```

```python title="Python"
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="unused")

stream = client.chat.completions.create(
    model="muse-glimmer",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a Python function to compute Fibonacci numbers."},
    ],
    max_tokens=2048,
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

Neither request sets sampling parameters, so the server applies the published settings from `--generation-config auto`.

## Verify tool calling {#tool-calling}

```bash title="curl"
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "muse-glimmer",
    "messages": [
      {"role": "user", "content": "What is the weather in Paris in celsius? Use the tool."}
    ],
    "tools": [{"type": "function", "function": {
      "name": "get_weather",
      "description": "Get current weather for a city.",
      "parameters": {"type": "object", "properties": {
        "city": {"type": "string"},
        "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}},
        "required": ["city"]}}}],
    "tool_choice": "auto"
  }'
```

You get back `get_weather(city="Paris", units="celsius")`, with the reasoning under `message.reasoning`, or `delta.reasoning` when streaming. Parsing happens server-side, so an OpenAI-compatible harness needs no [ATEM](/docs/muse-glimmer/prompting#tool-calling)-specific handling.

> [!IMPORTANT] One tool call per message
> Several calls arrive as consecutive assistant messages rather than as several entries in one `tool_calls` array. A harness that reads only the first element of the first message will silently drop work.

## Stop tokens {#stop-tokens}

Muse Glimmer needs `eos_token_id = [200001, 200008]`, which is `<|end_of_text|>` and `<|eot|>`. Serving with `--generation-config auto` picks these up from the checkpoint.

> [!WARNING] Never stop on the eom token
> Never stop on `<|eom|>` (200007). It ends a message while the turn continues, and it separates the reasoning block from each non-final tool call. Stopping on it can truncate the turn before later tool calls. Set this in the checkpoint's `generation_config.json`.

These token IDs come from the converted checkpoint. Confirm them against your checkpoint's `tokenizer_config.json`, since older exports can differ. See [special tokens](/docs/muse-glimmer/prompting#special-tokens) for the full chat-format token set.

## Troubleshooting {#troubleshooting}

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ValueError: model architectures ... are not supported` | Running a released vLLM wheel rather than the image | The model code isn't in any wheel. Use `vllm/vllm-openai:muse-glimmer`. |
| `invalid tool call parser` | Hyphenated parser name | Use underscores: `muse_glimmer`. |
| Tool calls returned as plain text | Parser not enabled | Pass `--tool-call-parser muse_glimmer`. The chat template comes from the checkpoint. |
| Only the first tool call runs | Harness expects one `tool_calls` array | One call per message. Read consecutive assistant messages. |
| Generation never stops | Wrong stop tokens | See [Stop tokens](#stop-tokens). Never stop on the end-of-message token. |
| Reasoning leaking into content | No reasoning parser | Pass `--reasoning-parser muse_glimmer`, which routes reasoning to `message.reasoning`. |
| Flat, repetitive answers | Running greedy | Drop `"temperature": 0` and use the published settings. |
| Out of memory shortly after startup | Sized to the 60 GB weights rather than the 72 GB serving footprint | Lower `--max-model-len`, raise `--tensor-parallel-size`, or serve a quantized checkpoint. |

## Next steps

Add [speculative decoding](/docs/muse-glimmer/spec-decode) to reduce per-token latency. For CPU or mixed inference, see [llama.cpp](/docs/muse-glimmer/llama-cpp); for other runtimes, see [Run inference](/docs/muse-glimmer/deploy).
