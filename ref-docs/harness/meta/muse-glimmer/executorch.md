---
meta:
  title: Deploy with ExecuTorch
  description: Export Muse Glimmer ahead of time and serve it on CUDA or Apple silicon with vision, tool calling, and DFlash speculative decoding.
  keywords: muse glimmer, ExecuTorch, DFlash, CUDA, MLX, tool calling
cms:
  alias: /model-api/docs/muse-glimmer/executorch
  target: aidmc
---

# Deploy with ExecuTorch

Serve Muse Glimmer on your own CUDA GPU or Apple silicon with [ExecuTorch](https://github.com/pytorch/executorch), behind an OpenAI-compatible HTTP endpoint that supports vision, tool calling, and DFlash speculative decoding. ExecuTorch is ahead-of-time: you export the model once into a `.pte` program for a specific backend, then serve from that program.

Each of the other [runtimes](/docs/muse-glimmer/deploy) reimplements the model by hand for every backend it supports. That approach scales for a plain text transformer. Muse Glimmer also carries multimodal input and block-diffusion speculative decoding, so each backend would need its own rewrite of all three. With ExecuTorch you write the model and its decoding strategy once in PyTorch, and `torch.export` lowers the whole graph ahead of time: to Triton on CUDA, and to MLX-native or custom Metal kernels on Apple silicon.

| Backend | Host | Artifacts written by a local export |
| --- | --- | --- |
| CUDA | Linux or Windows | `model.pte` plus `aoti_cuda_blob.ptd` |
| MLX | macOS on Apple silicon | Self-contained `model.pte` |

Prebuilt exports are published as well, under [different filenames](#prebuilt-export), so exporting a 30B model yourself is optional.

> [!IMPORTANT] No CPU export; use llama.cpp
> Use [llama.cpp](/docs/muse-glimmer/llama-cpp) on a CPU-only machine. ExecuTorch doesn't support CPU export for Muse Glimmer.

## Prerequisites {#prerequisites}

- An ExecuTorch checkout built from source per the [upstream guide](https://github.com/pytorch/executorch), including `examples/models/muse-glimmer`
- The server dependencies: `pip install -r examples/llm_server/python/requirements.txt`
- The Hugging Face CLI (`pip install huggingface_hub`)
- A CUDA GPU for the CUDA backend, or Apple silicon for the MLX backend

Run every command below from the ExecuTorch repository root.

## Download the model assets {#download-assets}

Exports lower directly from the quantized GGUF checkpoints, the same files [llama.cpp](/docs/muse-glimmer/llama-cpp) uses. The serving path also needs the tokenizer metadata from the main model repository:

```bash title="bash"
hf download meta-models/Muse-Glimmer-30B-GGUF --local-dir assets/quant \
  --include 'Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf' \
  --include 'dflash-Muse-Glimmer-30B-Q4_K_M.gguf' \
  --include 'mmproj-Muse-Glimmer-30B-Q4_K_M.gguf'

hf download meta-models/Muse-Glimmer-30B \
  tokenizer.json chat_template.jinja config.json processor_config.json \
  --local-dir assets/hf
```

Keep `chat_template.jinja` beside the rest of the tokenizer metadata: the serving path renders prompts and tool definitions with it.

Set the paths used by the commands that follow:

```bash title="bash"
TARGET=assets/quant/Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf
DRAFT=assets/quant/dflash-Muse-Glimmer-30B-Q4_K_M.gguf
MMPROJ=assets/quant/mmproj-Muse-Glimmer-30B-Q4_K_M.gguf
BACKEND=cuda   # mlx on macOS
```

## Export the model {#export}

`$BACKEND` selects the target: `cuda` or `mlx`. A CUDA export autotunes Triton kernels against the GPU it runs on, so export on the same architecture you intend to serve from.

### Target-only export {#target-export}

For text inference:

```bash title="bash"
python -m executorch.examples.models.muse_glimmer.export.export_solo \
  --gguf "$TARGET" \
  --backend "$BACKEND" \
  --output-dir exports/solo
```

### DFlash export {#dflash-export}

DFlash speculative decoding lowers the target and the draft together, into their own export directory:

```bash title="bash"
python -m executorch.examples.models.muse_glimmer.export.export_dflash \
  --target-gguf "$TARGET" \
  --draft-gguf "$DRAFT" \
  --backend "$BACKEND" \
  --output-dir exports/dflash
```

Both land in one `.pte`: the draft shares the target's token embeddings and output head rather than carrying copies. The block dimension is exported dynamically, so you select block length at serve time. The exported range is backend-specific: `[2, 16]` on MLX and `[2, 4]` on CUDA, where the draft count is also capped at 3.

### Vision exports {#vision-export}

Add `--mmproj "$MMPROJ"` to either export command for text and image inference. A vision export also writes `pos_embed.bin` beside `model.pte`.

### Download a prebuilt export {#prebuilt-export}

[`meta-models/Muse-Glimmer-30B-ExecuTorch-PTE`](https://huggingface.co/meta-models/Muse-Glimmer-30B-ExecuTorch-PTE) publishes 16 ready-made exports, which skips the export step. You still [build the runner](#build-runner): a `.pte` is a model program, not a runtime.

> [!WARNING] Download one export, not all
> Download a single directory with `--include` rather than the whole repository. The repository is 372 GB, and one export is 18–31 GB.

Directories are named `muse-glimmer-<quantization>-128K-<modality>-<decoding>-<backend>`, and all 16 combinations of the four axes exist:

- **Quantization**: `k-quant-17G` targets 24 GB of VRAM. `k-quant-dynamic` targets 32 GB with less degradation, and the [model card](https://huggingface.co/meta-models/Muse-Glimmer-30B-ExecuTorch-PTE) quantifies the tradeoff.
- **Modality**: `text`, or `text-image` for vision.
- **Decoding**: `solo`, or `dflash` for speculative decoding.
- **Backend**: `metal` for Apple silicon, `sm80+ptx` for CUDA on SM80 and newer.

Context length is `128K` for every variant. Sizes, by directory:

| Quantization | Modality | Decoding | `…-metal` | `…-sm80+ptx` |
| --- | --- | --- | --- | --- |
| `k-quant-17G` | `text` | `solo` | 17.9 GB | 19.8 GB |
| `k-quant-17G` | `text` | `dflash` | 19.6 GB | 27.2 GB |
| `k-quant-17G` | `text-image` | `solo` | 19.4 GB | 21.2 GB |
| `k-quant-17G` | `text-image` | `dflash` | 21.1 GB | 28.6 GB |
| `k-quant-dynamic` | `text` | `solo` | 20.7 GB | 22.6 GB |
| `k-quant-dynamic` | `text` | `dflash` | 22.4 GB | 30.0 GB |
| `k-quant-dynamic` | `text-image` | `solo` | 22.2 GB | 24.0 GB |
| `k-quant-dynamic` | `text-image` | `dflash` | 23.8 GB | 31.5 GB |

Each directory holds `<directory-name>.pte`. The `sm80+ptx` variants add `<directory-name>.ptd`, and the `text-image` variants add `pos_embed.bin`. On CUDA the weights live in the `.ptd` and the `.pte` is only tens of megabytes, so both files are required. The repository root carries the tokenizer metadata (`tokenizer.json`, `tokenizer_config.json`, and `chat_template.jinja`), so this one repository covers everything the server needs. The `assets/hf` download above is for the export path.

```bash title="bash"
EXPORT_DIR=muse-glimmer-k-quant-17G-128K-text-solo-sm80+ptx

hf download meta-models/Muse-Glimmer-30B-ExecuTorch-PTE \
  --include "$EXPORT_DIR/*" \
  --include tokenizer.json --include tokenizer_config.json --include chat_template.jinja \
  --local-dir exports
```

> [!IMPORTANT] Pass the actual export filenames
> Pass the downloaded filenames to `--model-path` and `--data-path`. A prebuilt directory names its artifacts after itself, so a download contains no `model.pte` and no `aoti_cuda_blob.ptd`.

## Build the runner {#build-runner}

```bash title="bash"
(cd examples/models/muse-glimmer && cmake --workflow --preset muse-glimmer-cuda)
```

Use the `muse-glimmer-mlx` preset on Apple silicon. Binaries land in `cmake-out/examples/models/muse-glimmer/`; the server needs `muse_glimmer_worker`.

## Serve the model {#serve}

```bash title="bash"
python -m executorch.examples.models.muse_glimmer.serving.serve \
  --model-path exports/solo/model.pte \
  --data-path exports/solo/aoti_cuda_blob.ptd \
  --tokenizer-path assets/hf/tokenizer.json \
  --hf-tokenizer assets/hf \
  --worker-bin cmake-out/examples/models/muse-glimmer/muse_glimmer_worker \
  --model-id muse-glimmer-30B \
  --tool-parser atem \
  --host 127.0.0.1 --port 8000
```

Adjust the command for your export:

- **MLX**: drop `--data-path`.
- **DFlash**: replace `exports/solo` with `exports/dflash` in both artifact paths. The server detects the exported method contract.
- **Vision**: add `--pos-embed-path <export-dir>/pos_embed.bin`.

From a [prebuilt export](#prebuilt-export), substitute the artifact and tokenizer flags. The rest of the command is unchanged:

```bash title="bash"
  --model-path "exports/$EXPORT_DIR/$EXPORT_DIR.pte" \
  --data-path "exports/$EXPORT_DIR/$EXPORT_DIR.ptd" \
  --tokenizer-path exports/tokenizer.json \
  --hf-tokenizer exports \
```

Drop `--data-path` for a `-metal` variant, which has no `.ptd`. Add `--pos-embed-path "exports/$EXPORT_DIR/pos_embed.bin"` for a `text-image` variant. A `-dflash` variant needs no extra flag.

Send a request to the running server:

```bash title="curl"
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "muse-glimmer-30B",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "max_tokens": 32,
    "temperature": 0
  }'
```

The server implements `/health`, `/v1/models`, and `/v1/chat/completions` (streaming and non-streaming). `--max-context` bounds the context window, and prompts over that bound are rejected with a 400.

## Verify tool calling {#tool-calling}

`--tool-parser atem` is what makes tool calling work end to end. The Hugging Face chat template renders your tool definitions, and the server converts Muse Glimmer's native [ATEM output](/docs/muse-glimmer/prompting#tool-calling) into an OpenAI-compatible `tool_calls` array, so your harness needs no Muse Glimmer-specific handling.

Two OpenAI parameters are rejected with a structured 400 rather than ignored:

- `reasoning_effort`: control reasoning with the chat template's [`reasoning_strength` argument](/docs/muse-glimmer/prompting#reasoning) instead.
- `tool_choice="required"`: `none`, `auto`, and unset are accepted.

## Stop tokens {#stop-tokens}

Muse Glimmer needs `eos_token_id = [<|end_of_text|>, <|eot|>]`. Never stop on `<|eom|>`, which ends a message while the turn continues. See [special tokens](/docs/muse-glimmer/prompting#special-tokens).

## Runtime limits {#limits}

These bound the runtime. The [model card](https://huggingface.co/meta-models/Muse-Glimmer-30B) covers the model itself.

- **No video input**: text and images only, one image per request.
- **No continuous batching**: one request runs at a time. `--num-runners` must be 1, the exported methods are batch-1, and execution is serialized. Concurrent sessions are isolated from each other rather than served in parallel.
- **No cross-session prefix sharing and no checkpointing**: every session holds its own KV cache, nothing is reused across sessions, and session state is discarded rather than saved.

For concurrent throughput from one machine, serve with [vLLM](/docs/muse-glimmer/vllm).

## Troubleshooting {#troubleshooting}

| Symptom | Cause | Fix |
| --- | --- | --- |
| Worker fails to load the method | Runner built without the quantized or custom-op kernels | Rebuild with the model's CMake workflow preset rather than a plain ExecuTorch build. |
| Tool calls arrive as plain text | Server started without `--tool-parser atem` | Restart with the flag. The default is `none`, which passes model output through unparsed. |
| `400` on a request that works elsewhere | Unsupported OpenAI parameter | See the rejected parameters in [Verify tool calling](#tool-calling). |
| Artifact not found on a downloaded export | Export filenames used against a prebuilt directory | A download has no `model.pte` or `aoti_cuda_blob.ptd`. Both artifacts are named after their directory. |

## Next steps

Compare runtimes on [Run inference](/docs/muse-glimmer/deploy), serve a team from GPUs with [vLLM](/docs/muse-glimmer/vllm), or run on a CPU-only machine with [llama.cpp](/docs/muse-glimmer/llama-cpp).
