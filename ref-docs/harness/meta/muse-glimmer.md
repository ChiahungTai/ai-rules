---
meta:
  title: Muse Glimmer
  description: Open-source multimodal model distilled from Muse Spark, built for local and edge deployment.
  keywords: muse glimmer, open source, local inference, distillation, llama, multimodal
cms:
  alias: /model-api/docs/muse-glimmer
  target: aidmc
---

# Muse Glimmer

[Muse Glimmer](/docs/models#muse-glimmer) is Meta's 30-billion-parameter open-source multimodal model, distilled from [Muse Spark](/docs/models#muse-spark) and built for local agentic workflows. Run it on your own hardware through supported runtimes. It ships with open weights, reads text and images, and reasons step by step before it answers.

Point your existing tooling at a local Muse Glimmer server and keep building — you own the weights, the runtime, and the data.

## Model variants {#model-variants}

| Model | Parameters | Architecture | Context window |
| --- | --- | --- | --- |
| Muse Glimmer | 30B | Dense, multimodal (text + image input; text output) | 128K tokens by default; longer contexts supported |

## Architecture {#architecture}

Muse Glimmer is a dense, decoder-only multimodal transformer with a built-in vision encoder. It is trained from Muse Spark's outputs rather than training from scratch. It accepts text and image input, produces text output, and has a default context window of 128K tokens with support for longer contexts.

## Supported languages {#supported-languages}

Muse Glimmer was trained on data from more than 100 languages.

## License {#license}

Muse Glimmer weights are released under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Launch partners {#launch-partners}

The Muse Glimmer launch ecosystem includes:

- AMD
- Arm
- Dell
- Fireworks AI
- Hugging Face
- Intel
- llama.cpp
- LM Studio
- NVIDIA
- Ollama
- OpenRouter
- SGLang and RadixArk
- Together AI
- Unsloth
- vLLM and Inferact

## Get started {#get-started}

<tile-group col="3">
<tile color="blue" icon="sparkle-diamond" href="/docs/muse-glimmer/get-the-model" title="Get the model">Download weights from Hugging Face and verify your setup.</tile>
<tile color="green" icon="cube" href="/docs/muse-glimmer/prompting" title="Prompting guide">Chat template, system prompts, and best practices for Muse Glimmer.</tile>
<tile color="purple" icon="monitor" href="/docs/muse-glimmer/deploy" title="Run inference">Pick a runtime: vLLM, SGLang, llama.cpp, or ExecuTorch.</tile>
</tile-group>

## Next steps

Now that you know what Muse Glimmer offers, [get the model](/docs/muse-glimmer/get-the-model) and run your first inference. If you're ready to optimize, explore [quantization](/docs/muse-glimmer/quantization) to fit the model on smaller hardware, or [speculative decoding](/docs/muse-glimmer/spec-decode) to accelerate generation. To adapt Muse Glimmer to your domain, see [customization](/docs/muse-glimmer/customization).
