---
meta:
  title: Run inference
  description: Run Muse Glimmer on your own infrastructure or through a hosted cloud provider.
  keywords: muse glimmer, inference, deployment, cloud inference, together ai
cms:
  alias: /model-api/docs/muse-glimmer/deploy
  target: aidmc
---

# Run inference

Run Muse Glimmer on your own infrastructure or call it through a hosted cloud provider. The self-hosted runtimes below load the released checkpoints (or a quantized version of them) and use the Muse Glimmer chat format described in the [prompting guide](/docs/muse-glimmer/prompting).

| Runtime | Best for | Hardware | Serving API |
| --- | --- | --- | --- |
| [vLLM](/docs/muse-glimmer/vllm) | Production serving, high throughput | NVIDIA GPU (single or multi) | OpenAI-compatible HTTP |
| [SGLang](/docs/muse-glimmer/sglang) | High-throughput serving for concurrent users | NVIDIA GPU, Apple silicon | OpenAI-compatible HTTP |
| [llama.cpp](/docs/muse-glimmer/llama-cpp) | Local and mixed CPU/GPU, laptops | CPU, NVIDIA/AMD GPU, Apple Metal | OpenAI-compatible HTTP + CLI |
| [ExecuTorch](/docs/muse-glimmer/executorch) | Ahead-of-time export, local serving | NVIDIA GPU on Linux or Windows, Apple silicon on macOS | OpenAI-compatible HTTP |

> [!NOTE] Stream reasoning workloads
> Muse Glimmer produces long chain-of-thought reasoning by default. For reasoning workloads, request streaming (`stream: true`) so long generations don't hit request timeouts. See [prompting](/docs/muse-glimmer/prompting#reasoning) and [Deploy with vLLM](/docs/muse-glimmer/vllm).

<tile-group col="2">
<tile color="purple" icon="monitor" href="/docs/muse-glimmer/vllm" title="Deploy with vLLM">Production-grade throughput with an OpenAI-compatible endpoint.</tile>
<tile color="teal" icon="cloud" href="/docs/muse-glimmer/sglang" title="Deploy with SGLang">High-throughput serving for concurrent users.</tile>
<tile color="blue" icon="cube" href="/docs/muse-glimmer/llama-cpp" title="Deploy with llama.cpp">Run locally on CPU, GPU, or a mix.</tile>
<tile color="green" icon="diamonds-stacked" href="/docs/muse-glimmer/executorch" title="Deploy with ExecuTorch">Export ahead of time for CUDA or Apple silicon.</tile>
</tile-group>

## Run inference on cloud {#run-inference-on-cloud}

Use Together AI to call Muse Glimmer through a hosted API without managing model infrastructure.

<tile-group col="2">
<tile color="orange" icon="cloud" href="/docs/muse-glimmer/together-ai" title="Run with Together AI">Set up authentication and send your first hosted inference request.</tile>
</tile-group>

## Next steps

Once you have picked a runtime or provider, tune your prompts with the [prompting guide](/docs/muse-glimmer/prompting), shrink the model with [quantization](/docs/muse-glimmer/quantization), or speed up self-hosted generation with [speculative decoding](/docs/muse-glimmer/spec-decode).
