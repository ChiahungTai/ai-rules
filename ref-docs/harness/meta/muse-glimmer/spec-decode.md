---
meta:
  title: Speculative decoding
  description: Accelerate Muse Glimmer inference with DFlash speculative decoding on llama.cpp, SGLang, and ExecuTorch.
  keywords: muse glimmer, speculative decoding, dflash, inference speed, latency
cms:
  alias: /model-api/docs/muse-glimmer/spec-decode
  target: aidmc
---

# Speculative decoding

Speed up Muse Glimmer with DFlash, its block-diffusion speculative decoding. A small draft model proposes continuation tokens and Muse Glimmer verifies them, so more than one token can land per verification step. That helps most on Muse Glimmer's long reasoning traces, where single-request latency dominates.

DFlash is set up per runtime. This page covers what the drafts are and where each runtime documents the flags.

## Draft checkpoints {#draft-checkpoints}

Two draft artifacts are published. The runtime-specific guide determines which one to use:

| Draft | Where it lives | Use it with |
| --- | --- | --- |
| `meta-models/Muse-Glimmer-30B-assistant` | Its own repository. Serves as published, with no conversion step. | SGLang's documented BF16, GGUF, and NVFP4 paths |
| `dflash-Muse-Glimmer-30B-Q4_K_M.gguf` | [`meta-models/Muse-Glimmer-30B-GGUF`](https://huggingface.co/meta-models/Muse-Glimmer-30B-GGUF), roughly 1.6 GB | llama.cpp, ExecuTorch exports, and SGLang's GGUF-draft path |

## Set it up on your runtime {#runtimes}

| Runtime | How DFlash is enabled |
| --- | --- |
| [llama.cpp](/docs/muse-glimmer/llama-cpp#server) | Add `-md` with the GGUF draft, plus `--spec-type draft-dflash` and its draft flags, to the serve command. |
| [SGLang](https://docs.sglang.io/cookbook/autoregressive/Meta/MuseGlimmer) | Pass `--speculative-algorithm DFLASH` with a draft model path and block size. Not available on the MLX backend, and the draft needs its own memory headroom. |
| [ExecuTorch](/docs/muse-glimmer/executorch#dflash-export) | Export target and draft together with `export_dflash`. They land in one program, because the draft shares the target's token embeddings and output head rather than carrying copies. |

Each runtime exposes its own draft-length and block-size knobs, and the useful values depend on the backend and hardware. The runtime pages carry the current flags and their limits.

## Next steps

Combine speculative decoding with [quantization](/docs/muse-glimmer/quantization) for maximum efficiency on limited hardware. For production deployment, see [Run inference](/docs/muse-glimmer/deploy).
