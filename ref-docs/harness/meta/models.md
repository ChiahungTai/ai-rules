---
meta:
  title: Models
  description: The Muse model families on Meta Model API, spanning Muse Spark, Muse Image, Muse Voice Transcribe, and the open-weight Muse Glimmer, and how to choose the right model.
  keywords: models, Muse Spark, Muse Image, Muse Voice Transcribe, Muse Glimmer, speech to text, transcription, image generation, open weights, contributor tier, pricing tier, model selection, model lineup, context window
cms:
  alias: /model-api/docs/models
  target: aidmc
---

# Models

Meta ships four model families. **Muse Spark**, **Muse Image**, and **Muse Voice Transcribe** are hosted on Meta Model API and called over the endpoints in these docs; **Muse Glimmer** is open-weight and runs on your own hardware. This page summarizes each and points you to where to go next.

## Muse Spark {#muse-spark}

Muse Spark is Meta's model for agentic and coding work — multi-step tool loops, software engineering assistants, and long-context reasoning. Three model IDs serve the family:

| Model ID | Tier | Input modalities | Output modalities | Context window |
| :---- | :---- | :---- | :---- | :---- |
| `muse-spark-1.1` | [Standard](/docs/pricing-rate-limits#standard-tier) | Text, image, video, PDF | Text | 1,048,576 tokens |
| `muse-spark-1.2` | [Standard](/docs/pricing-rate-limits#standard-tier) | Text, image, video, PDF | Text | 1,048,576 tokens |
| `muse-spark-1.2-contributor` | [Contributor](/docs/pricing-rate-limits#contributor-tier) | Text, image, video, PDF | Text | 1,048,576 tokens |

All three IDs serve the Muse Spark family and share modalities and a 1,048,576-token context window. They differ by checkpoint and **tier**:

- **`muse-spark-1.1`** — the earlier checkpoint, on the **[Standard](/docs/pricing-rate-limits#standard-tier)** tier.
- **`muse-spark-1.2`** — an updated checkpoint with slightly higher performance, also on the **[Standard](/docs/pricing-rate-limits#standard-tier)** tier.
- **`muse-spark-1.2-contributor`** — the `muse-spark-1.2` checkpoint on the discounted **[Contributor](/docs/pricing-rate-limits#contributor-tier)** tier, where your prompts and completions may be used to train future Meta models.

`muse-spark-1.2` is the default model in the code examples throughout these docs.

Muse Spark is multimodal: it takes text, image, video, audio, and PDF as input and generates text. Use it for [chat completion](/docs/protocols/chat-completions), [image understanding](/docs/image-understanding), [video and audio understanding](/docs/video-understanding), [tool calling](/docs/tool-calling), [structured output](/docs/structured-output), and [search grounding](/docs/search-grounding).

Use [Muse Voice Transcribe](#muse-voice-transcribe) instead when you need a dedicated speech-to-text API for live or file transcription.

### Tiers {#tiers}

Tier is a model attribute: it sets the price you pay and whether your data may be used to train future Meta models.

- **[Standard](/docs/pricing-rate-limits#standard-tier)** (`muse-spark-1.1`, `muse-spark-1.2`) — standard pricing; your prompts and completions are not used to train Meta models.
- **[Contributor](/docs/pricing-rate-limits#contributor-tier)** (`muse-spark-1.2-contributor`) — heavily discounted pricing in exchange for permission to use your prompts and completions to train future Meta models.

The [contributor tier](/docs/pricing-rate-limits#contributor-tier) lowers the barrier to entry: it gives you room to prototype, test integrations, and scale experiments without the usual cost overhead, in return for permission to train on your data.

See [Pricing and rate limits](/docs/pricing-rate-limits) for per-tier pricing and model availability.

## Muse Image {#muse-image}

Muse Image is a separate model family that **outputs images** rather than text. Send a text prompt (and optional reference images) and get an image back, or send an image with an instruction to edit it. One model handles both generation and editing. It's agentic, so it can search the web for visual references and current facts and run code to build layouts before it renders.

| Model ID | Family | Input | Output |
| :---- | :---- | :---- | :---- |
| `muse-image-1.0` | Muse Image | Text, image | Image |

Reach Muse Image two ways: the [Responses API](/docs/protocols/responses) for conversational, multi-turn editing, or the single-shot [`/v1/images/generations`](/docs/api-reference/images/create-image) and [`/v1/images/edits`](/docs/api-reference/images/edit-image) endpoints for one-off calls. See the [Image generation](/docs/image-generation) guide to get started.

## Muse Voice Transcribe {#muse-voice-transcribe}

Muse Voice Transcribe is Meta's speech-to-text model on Meta Model API. Use it to transcribe live audio streams or supported audio files.

| Model ID | Family | Input | Output |
| :---- | :---- | :---- | :---- |
| `muse-voice-transcribe-1.0` | Muse Voice Transcribe | Audio | Text transcript |

Muse Voice Transcribe is built for real-time speech products: voice agents, meeting and call intelligence, live transcription, dictation, captioning, and high-volume transcription. It supports streaming speaker diarization, native endpointing and voice activity detection, contextual and keyword biasing, 25 evaluated languages with code-switching, and turn-level timestamps.

It returns transcript text. It does not synthesize speech or provide a speech-to-speech conversation API. It does not provide word-level timestamps, sound event detection, or emotion detection.

Reach Muse Voice Transcribe two ways: the realtime WebSocket endpoint (`wss://api.meta.ai/v1/asr/realtime`) for live audio, or the file endpoint ([`POST /v1/asr/transcribe`](/docs/api-reference/voice/transcribe)) for a recording you already have.

Start with the [Muse Voice Transcribe guide](/docs/speech-to-text). See [Pricing and rate limits](/docs/pricing-rate-limits#muse-voice-transcribe-pricing) for audio pricing.

## Muse Glimmer {#muse-glimmer}

Muse Glimmer is Meta's open-weight multimodal model, distilled from Muse Spark and built to run on your own hardware. Unlike Muse Spark, Muse Image, and Muse Voice Transcribe, you don't call it over Model API — you download the weights and serve it through a runtime such as vLLM, SGLang, llama.cpp, or ExecuTorch.

Because it's self-hosted, Muse Glimmer has its own documentation section covering how to get the model, prompt it, deploy it, and customize it — rather than the API tiers and specs listed above.

- **[Muse Glimmer overview](/docs/muse-glimmer)**: variants, architecture, license, and launch partners.
- **[Get the model](/docs/muse-glimmer/get-the-model)**: download the weights and verify your setup.
- **[Run inference](/docs/muse-glimmer/deploy)**: pick a runtime and serve it locally.

## List models via the API {#list-models}

Query the catalog programmatically when you need to check what's enabled for your team. This returns the API-hosted models (Muse Spark and Muse Image); Muse Glimmer is open-weight and isn't served through this endpoint.

```python title="Python (OpenAI SDK)"
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

response = client.models.list()

print(response.model_dump_json(indent=2))
```
```python title="Python (requests)"
import json
import os

import requests

response = requests.get(
    "https://api.meta.ai/v1/models",
    headers={"Authorization": f"Bearer {os.environ['MODEL_API_KEY']}"},
)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
```
```shell title="curl"
curl -X GET "https://api.meta.ai/v1/models" \
  -H "Authorization: Bearer $MODEL_API_KEY"
```


The response returns models sorted newest-first by creation time, with the model ID as a stable tiebreaker. Each object includes a `created` field — the Unix timestamp in seconds for when the model was added to the registry. `GET /v1/models/{model}` returns the same `created` value for a single model.

## Next steps

- [Get started](/docs/quickstart#first-call): make your first call with Muse Spark
- [Pricing and rate limits](/docs/pricing-rate-limits): see rates and retry guidance
- [Chat completion](/docs/protocols/chat-completions): start generating with the core conversational endpoint
