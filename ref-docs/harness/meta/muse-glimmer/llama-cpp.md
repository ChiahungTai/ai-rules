---
meta:
  title: Deploy with llama.cpp
  description: Run Muse Glimmer locally with llama.cpp for CPU, mixed, and GPU inference.
  keywords: muse glimmer, llama.cpp, local inference, deployment
cms:
  alias: /model-api/docs/muse-glimmer/llama-cpp
  target: aidmc
---

# Deploy with llama.cpp

Run Muse Glimmer on your machine with [llama.cpp](https://github.com/ggml-org/llama.cpp), a C/C++ inference engine that supports CPU, mixed CPU/GPU, and full GPU execution. It's portable across CPU, Metal, CUDA, ROCm, and Vulkan, and it serves the published GGUF checkpoints with no conversion or quantization step.

> [!IMPORTANT] Upstream is the source of truth
> [`ggml-org/llama.cpp`](https://github.com/ggml-org/llama.cpp) is the source of truth for builds, flags, and releases. Muse Glimmer support landed in commit [`62bf73d25`](https://github.com/ggml-org/llama.cpp/commit/62bf73d25) ("model: Muse Glimmer Support", PR #26841), which adds the `muse-glimmer` architecture, the vision projector, the ATEM tool-call parser, and DFlash speculative decoding. Check upstream first when a command here doesn't match what you see.

## Download the checkpoints {#download-checkpoints}

GGUF builds live in [`meta-models/Muse-Glimmer-30B-GGUF`](https://huggingface.co/meta-models/Muse-Glimmer-30B-GGUF). Fetch only the two files you need: the text model and, for image input, the vision projector.

```bash title="bash"
pip install -U huggingface_hub
hf download meta-models/Muse-Glimmer-30B-GGUF --local-dir ./muse-glimmer \
  --include "Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf" \
  --include "mmproj-Muse-Glimmer-30B-Q4_K_M.gguf"
```

| File | What | Size |
| --- | --- | --- |
| `Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf` | Text model, K-quant. Use this one. | ~17 GB |
| `Muse-Glimmer-30B-KQuant-Dynamic-Q4_K_XL.gguf` | Text model, dynamic K-quant | ~20 GB |
| `mmproj-Muse-Glimmer-30B-Q4_K_M.gguf` | Vision projector, needed for image input | ~1.4 GB |
| `dflash-Muse-Glimmer-30B-Q4_K_M.gguf` | Speculative-decode draft model, optional | ~1.6 GB |

Full-precision weights aren't published as GGUF. For bf16, use the safetensors checkpoint at [`meta-models/Muse-Glimmer-30B`](https://huggingface.co/meta-models/Muse-Glimmer-30B) with [vLLM](/docs/muse-glimmer/vllm).

## Get llama.cpp {#get-llama-cpp}

Muse Glimmer support first shipped in release [`b10353`](https://github.com/ggml-org/llama.cpp/releases/tag/b10353). Use `b10353` or newer. A prebuilt binary and a source build both work.

> [!IMPORTANT] Use build b10353 or newer
> `b10344` and older don't register the `muse-glimmer` architecture and refuse to load these checkpoints. The load error is shown below.
> `llama-server --version` prints the build number to check against: `version: 10353 (...)` or higher.

```
llama_model_load: error loading model: unknown model architecture: 'muse-glimmer'
```

The [releases page](https://github.com/ggml-org/llama.cpp/releases) publishes prebuilt binaries for macOS arm64 (Metal), Linux (CPU, CUDA, ROCm, Vulkan, SYCL), and Windows. If you take one, unpack it and skip to [Start the server](#server), reading `./build/bin/` in the commands below as the directory you unpacked.

To build from source instead, `master` is well past the floor:

```bash title="bash"
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Add `--branch b10353` to pin to the floor, or any later tag to pin to a known build.

Pick your backend:

```bash title="bash"
# Apple silicon (Metal)
cmake -B build -DGGML_METAL=ON -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF

# NVIDIA (CUDA >= 12.4; set the arch for your card, 90 = Hopper, 120 = Blackwell)
cmake -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=OFF \
  -DCMAKE_CUDA_ARCHITECTURES=90 \
  -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF

# CPU only
cmake -B build -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF
```

```bash title="bash"
cmake --build build -j"$(sysctl -n hw.ncpu)" --target llama-server llama-cli llama-mtmd-cli   # macOS
cmake --build build -j"$(nproc)"             --target llama-server llama-cli llama-mtmd-cli   # Linux
```

> [!IMPORTANT] Keep the Web UI build off
> Keep `-DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF` unless you need the browser Web UI. The UI build fetches assets over the network and fails behind restrictive proxies or without Node.js. The HTTP API is unaffected.

If `ccache` errors during the build, add `-DGGML_CCACHE=OFF`.

Confirm the checkout registers the architecture before you go looking for other reasons a load failed:

```bash title="bash"
grep -c LLM_ARCH_MUSE_GLIMMER src/llama-arch.cpp   # expect >= 1
```

A `0` means the checkout predates Muse Glimmer support and will refuse these files.

Run the commands below from the `llama.cpp` clone (or the unpacked release directory), with the `muse-glimmer/` download directory inside it, so both `./build/bin/` and `./muse-glimmer/` resolve. Otherwise pass absolute paths to `-m` and `--mmproj`.

## Start the server {#server}

Muse Glimmer supports a native context of 131072:

```bash title="bash"
./build/bin/llama-server \
  -m ./muse-glimmer/Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf \
  --mmproj ./muse-glimmer/mmproj-Muse-Glimmer-30B-Q4_K_M.gguf \
  -a muse-glimmer \
  -ngl 99 -c 131072 -np 1 \
  --host 127.0.0.1 --port 8080 --api-key <your-key> \
  --jinja \
  --chat-template-kwargs '{"reasoning_strength":"low"}'
```

The server prints the context you actually got:

```
srv load_model: initializing, n_slots = 1, n_ctx_slot = 131072, kv_unified = 'false'
```

If it instead reports `exceeds the training context ... - capping`, the GGUF's `context_length` metadata is stale and the server clamps the slot to it. No serve flag overrides this. Fix the metadata with the script in the llama.cpp clone, where `muse-glimmer` is the architecture name llama.cpp registers and so is the key prefix:

```bash title="bash"
python gguf-py/gguf/scripts/gguf_set_metadata.py <model>.gguf muse-glimmer.context_length 131072
```

| Flag | Why |
| --- | --- |
| `--jinja` | Applies the Muse Glimmer control-token template embedded in the GGUF. Without it, tool calling and reasoning separation break. |
| `-a muse-glimmer` | The name the API answers to. Without it the alias is the checkpoint path, and the `"model": "muse-glimmer"` every example here sends won't match. |
| `--chat-template-kwargs` | Sets `reasoning_strength`. Template default is `high`. |
| `-np N` | Concurrent slots, and the context is divided N ways: `-np 4` with `-c 131072` gives each slot 32768. Long-context agents want `-np 1`. See [Context per slot](#context-per-slot). |
| `-ngl 99` | Offload all layers to the GPU. |
| `--api-key` | Guards inference endpoints only. `/health` and `/v1/models` still answer without it. |

Thinking lands in `message.reasoning_content` and `message.content` stays clean. That's the server default, with no flag needed. Pass `--reasoning-format none` to keep thinking inline in `message.content` instead.

Drop `--mmproj` for text-only. For speculative decoding add `-md <draft>.gguf --spec-type draft-dflash -ngld 99 --spec-draft-n-max 4`. A `[spec] failed to measure draft model memory` warning at startup is harmless, and the draft loads and serves normally after it.

> [!NOTE] Don't override the chat template
> Don't pass `--chat-template-file`. Upstream ships no Muse Glimmer template under `models/templates/`, and none is needed: `--jinja` uses the template embedded in the GGUF, which is byte-for-byte identical to the `chat_template.jinja` published with the safetensors checkpoint. llama.cpp selects the ATEM tool-call parser by detecting that template, so tool calling works from `--jinja` alone.

Smoke test, where `--noproxy` bypasses a proxy that would intercept loopback:

```bash title="curl"
curl -s --noproxy '*' http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" -H "Authorization: Bearer <your-key>" \
  -d '{"model":"muse-glimmer","messages":[{"role":"user","content":"What is 17 * 23?"}],"temperature":0}'
```

### Context per slot {#context-per-slot}

`n_ctx_slot` in the startup log, not `-c`, is what bounds a single generation. Getting this wrong fails quietly: a generation that runs out of room produces no answer and no error, so a batch job or an eval reports a worse number and gives you nothing to debug.

Muse Glimmer reasons at length, which makes the margin thinner than it looks. A single generation can approach a 32768-token slot on its own. To keep concurrency without shrinking the slot, scale `-c` with `-np`:

```bash title="bash"
  -c 524288 -np 4        # 131072 per slot, still 4-way concurrent
```

KV cache stays affordable at that size: GQA with 2 KV heads, and sliding-window attention on three of every four layers.

### Controlling reasoning length {#reasoning-length}

The chat template reads `reasoning_strength` and defaults to `high`:

```jinja title="jinja"
{%- set rs = reasoning_strength if reasoning_strength is defined and reasoning_strength else 'high' -%}
```

Set it server-wide with `--chat-template-kwargs`, or per request:

```json title="JSON"
{"model":"muse-glimmer","messages":[],"chat_template_kwargs":{"reasoning_strength":"low"}}
```

The model card documents four levels: `low`, `medium`, `high`, and `xhigh`. Lower isn't automatically worse: where the environment validates the answer or the caller can retry cheaply, extra reasoning buys little. Reasoning tokens count against `max_tokens`, and a request that hits the ceiling mid-thought returns empty `content` with `finish_reason: "length"`.

> [!NOTE] Use reasoning_strength, not reasoning_effort
> `reasoning_effort`, the OpenAI spelling, is not implemented by llama.cpp. Use `chat_template_kwargs.reasoning_strength`, which is the same control the [prompting guide](/docs/muse-glimmer/prompting#reasoning) documents.

Reasoning can't be turned off here. The template opens the thinking channel unconditionally, so `--reasoning off` and `"reasoning_effort": "none"` both leave the output unchanged. `reasoning_strength: low` is how you spend fewer thinking tokens, and `--reasoning-budget N` is how you hard-cap them.

### Vision {#vision}

Send a remote URL, a `data:image/...;base64,...` URI, or a local path:

```bash title="curl"
curl -s --noproxy '*' http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" -H "Authorization: Bearer <your-key>" \
  -d '{"model":"muse-glimmer","messages":[{"role":"user","content":[
        {"type":"text","text":"What is in this image?"},
        {"type":"image_url","image_url":{"url":"data:image/png;base64,..."}}
      ]}],"temperature":0}'
```

Images are billed as prompt tokens, scaling with resolution.

## Command line, without the server {#cli}

The build produces two CLI binaries alongside `llama-server`. Text goes through `llama-cli`:

```bash title="bash"
./build/bin/llama-cli \
  -m ./muse-glimmer/Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf \
  -ngl 99 -c 32768 --jinja -st
```

`-st` (`--single-turn`) answers once and exits. Without it, `llama-cli` stays interactive and waits on stdin, which reads as a hang.

For images, use `llama-mtmd-cli`:

```bash title="bash"
./build/bin/llama-mtmd-cli \
  -m       ./muse-glimmer/Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf \
  --mmproj ./muse-glimmer/mmproj-Muse-Glimmer-30B-Q4_K_M.gguf \
  -ngl 99 -c 32768 --jinja \
  --image photo.png -p "Describe this image."
```

`--jinja` is required here too. Without it, `llama-mtmd-cli` aborts with `this custom template is not supported, try using --jinja`.

Both CLIs print the thinking trace inline with the answer, and neither separates the two. `--reasoning-format` only applies to the server's JSON response, so use `llama-server` when you want `content` and `reasoning_content` apart.

## Verify tool calling {#tool-calling}

```bash title="curl"
curl -s --noproxy '*' http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" -H "Authorization: Bearer <your-key>" \
  -d '{"model":"muse-glimmer","messages":[{"role":"user","content":"What is the weather in Paris in celsius? Use the tool."}],
       "tools":[{"type":"function","function":{
         "name":"get_weather","description":"Get current weather for a city.",
         "parameters":{"type":"object","properties":{
           "city":{"type":"string"},"units":{"type":"string","enum":["celsius","fahrenheit"]}},
           "required":["city"]}}}],
       "tool_choice":"auto","temperature":0}'
```

Returns `finish_reason: "tool_calls"` and a `tool_calls` array with `get_weather(city="Paris", units="celsius")`, with reasoning under `reasoning_content`. Parsing is server-side, so any OpenAI-compatible harness needs no [ATEM](/docs/muse-glimmer/prompting#tool-calling)-specific handling.

## Stop tokens {#stop-tokens}

Muse Glimmer needs `eos_token_id = [<|end_of_text|>, <|eot|>]`. Never stop on `<|eom|>`. The template handles this, and `--jinja` is what wires it up. See [special tokens](/docs/muse-glimmer/prompting#special-tokens).

## Next steps

For faster generation, add [speculative decoding](/docs/muse-glimmer/spec-decode) with a smaller draft model. To quantize the model yourself, see [quantization](/docs/muse-glimmer/quantization); for other runtimes, see [Run inference](/docs/muse-glimmer/deploy).
