---
meta:
  title: Get the model
  description: Download Muse Glimmer weights and artifacts from Hugging Face and pick the build your runtime needs.
  keywords: muse glimmer, download, huggingface, weights, gguf, setup
cms:
  alias: /model-api/docs/muse-glimmer/get-the-model
  target: aidmc
---

# Get the model

Download Muse Glimmer from Hugging Face and pick the build that matches your runtime. Everything runs offline once the weights land: there's no API key and no gated access.

## Prerequisites {#prerequisites}

- Python 3.10 or later
- The Hugging Face CLI: `pip install -U huggingface_hub`

## Choose an artifact {#choose-an-artifact}

Four repositories cover the published builds. Which one you want follows the runtime you plan to serve with:

| Repository | What it holds | Use it with |
| --- | --- | --- |
| [`meta-models/Muse-Glimmer-30B`](https://huggingface.co/meta-models/Muse-Glimmer-30B) | The bf16 safetensors checkpoint, tokenizer, chat template, and processor config. Around 60 GB. | [vLLM](/docs/muse-glimmer/vllm), [SGLang](/docs/muse-glimmer/sglang) |
| [`meta-models/Muse-Glimmer-30B-GGUF`](https://huggingface.co/meta-models/Muse-Glimmer-30B-GGUF) | Quantized GGUF builds, plus the vision projector and the GGUF draft model. | [llama.cpp](/docs/muse-glimmer/llama-cpp), [ExecuTorch](/docs/muse-glimmer/executorch) exports, [SGLang](/docs/muse-glimmer/sglang) |
| [`meta-models/Muse-Glimmer-30B-assistant`](https://huggingface.co/meta-models/Muse-Glimmer-30B-assistant) | The DFlash draft checkpoint. Serves as published, with no conversion step. | [Speculative decoding](/docs/muse-glimmer/spec-decode) |
| [`meta-models/Muse-Glimmer-30B-ExecuTorch-PTE`](https://huggingface.co/meta-models/Muse-Glimmer-30B-ExecuTorch-PTE) | Prebuilt ExecuTorch `.pte` exports, so you can skip exporting a 30B model yourself. | [ExecuTorch](/docs/muse-glimmer/executorch#prebuilt-export) |

The files inside the GGUF repository:

| File | What | Size |
| --- | --- | --- |
| `Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf` | Text model, K-quant. Smaller footprint — fits under 24 GB VRAM. | ~17 GB |
| `Muse-Glimmer-30B-KQuant-Dynamic-Q4_K_XL.gguf` | Text model, dynamic K-quant. Higher quality — for 32 GB VRAM. | ~20 GB |
| `mmproj-Muse-Glimmer-30B-Q4_K_M.gguf` | Vision projector, needed for image input | ~1.4 GB |
| `dflash-Muse-Glimmer-30B-Q4_K_M.gguf` | Speculative-decode draft model, optional | ~1.6 GB |

## Download {#download}

The bf16 checkpoint, for vLLM and SGLang:

```bash title="bash"
hf download meta-models/Muse-Glimmer-30B --local-dir ./muse-glimmer-30b
```

The GGUF builds, fetching only the files you need:

```bash title="bash"
hf download meta-models/Muse-Glimmer-30B-GGUF --local-dir ./muse-glimmer \
  --include "Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf" \
  --include "mmproj-Muse-Glimmer-30B-Q4_K_M.gguf"
```

Add `--include "dflash-Muse-Glimmer-30B-Q4_K_M.gguf"` for the GGUF draft model.

The DFlash draft checkpoint:

```bash title="bash"
hf download meta-models/Muse-Glimmer-30B-assistant --local-dir ./muse-glimmer-assistant
```

> [!WARNING] Download one export, not all
> Download a single directory from the prebuilt ExecuTorch repository with `--include`, not the whole repository. It publishes 16 exports and is far larger than any one of them. [Deploy with ExecuTorch](/docs/muse-glimmer/executorch#prebuilt-export) has the naming scheme and the command.

## Check the tokenizer {#tokenizer}

The main repository ships the tokenizer, `chat_template.jinja`, `config.json`, and `processor_config.json`, so it carries everything a runtime needs to frame prompts. Load the tokenizer and render a prompt to confirm the download is usable:

```python title="Python"
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("meta-models/Muse-Glimmer-30B")

messages = [{"role": "user", "content": "In one sentence, what is Muse Glimmer good at?"}]
print(tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=False))
```

The rendered prompt uses Muse Glimmer's channel-scoped framing (`<|start|>`, `<|message|>`, `<|eot|>`), which the [prompting guide](/docs/muse-glimmer/prompting#chat-template) covers.

> [!NOTE] Requires transformers 5.15 or later
> Use `transformers` 5.15 or later. Earlier versions lack the native Muse Glimmer path and prompt for `trust_remote_code`.

## Next steps

With the weights downloaded, set up your [prompting format](/docs/muse-glimmer/prompting) to get the best results from Muse Glimmer. When you're ready to serve, [pick a runtime](/docs/muse-glimmer/deploy): vLLM, SGLang, llama.cpp, or ExecuTorch.
