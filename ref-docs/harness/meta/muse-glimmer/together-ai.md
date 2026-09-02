---
meta:
  title: Together AI
  description: Run Muse Glimmer through Together AI's managed chat completions API.
  keywords: muse glimmer, together ai, hosted inference, cloud inference, deployment
cms:
  alias: /model-api/docs/muse-glimmer/together-ai
  target: aidmc
---

# Together AI

Together AI serves Muse Glimmer as a managed API. There are no weights to download, no runtime to install, and no GPU to own. You send requests to `https://api.together.xyz/v1/chat/completions` with a model string and an API key.

**This page requires an API key.** That is the trade the self-hosted guides don't make; see [Run inference](/docs/muse-glimmer/deploy) for those options.

Everything under "What Together publishes" is taken from Together's [Muse Glimmer model page](https://www.together.ai/models/muse-glimmer), read on 2026-08-11. Anything Together measured but doesn't publish there is marked as theirs.

## The model string {#model-string}

```plaintext title="Plaintext"
meta-models/Muse-Glimmer-30B
```

That string is the whole integration. It is what Together lists as the endpoint on the model page, and it's what appears in all three of their published examples.

## What Together publishes {#published-details}

| | |
| --- | --- |
| Endpoint | `meta-models/Muse-Glimmer-30B` |
| Provider | Meta |
| Type | Chat, Vision |
| Deployment | Serverless, Dedicated |
| Parameters | 30B |
| Context length | 128K+ |
| Input modalities | Text, Image |
| Output modalities | Text |
| Input price | $0.35 / 1M tokens ($0.04 / 1M cached) |
| Output price | $1.50 / 1M tokens |
| Released | August 10, 2026 |
| License | Apache 2.0 |
| Availability | 99.9% SLA, serverless and dedicated |

Tool calling is supported through the model's chat template, which makes this endpoint usable for the agent loops described in the [tool-calling guide](/docs/muse-glimmer/prompting#tool-calling).

## Get a key {#get-a-key}

```bash title="bash"
export TOGETHER_API_KEY=...   # https://api.together.xyz/settings/api-keys
```

Check that it works and that the model is visible to your account:

```bash title="bash"
curl -s https://api.together.xyz/v1/models \
  -H "Authorization: Bearer $TOGETHER_API_KEY" | grep -o 'meta-models/Muse-Glimmer-30B'
```

## Call it {#call-it}

Together publishes three clients. The curl form shows the wire format:

```bash title="curl"
curl -X POST "https://api.together.xyz/v1/chat/completions" \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-models/Muse-Glimmer-30B",
    "messages": [
      {"role": "user", "content": "What are some fun things to do in New York?"}
    ]
  }'
```

Python, using Together's official SDK (`pip install together`; it reads `TOGETHER_API_KEY` from the environment):

```python title="Python"
from together import Together

client = Together()
response = client.chat.completions.create(
    model="meta-models/Muse-Glimmer-30B",
    messages=[{"role": "user", "content": "What are some fun things to do in New York?"}],
)
print(response.choices[0].message.content)
```

TypeScript, using `together-ai`:

```javascript title="JavaScript"
import Together from 'together-ai';

const together = new Together();
const completion = await together.chat.completions.create({
  model: 'meta-models/Muse-Glimmer-30B',
  messages: [{ role: 'user', content: 'What are some fun things to do in New York?' }],
});
console.log(completion.choices[0].message.content);
```

The path, bearer header, and `{model, messages}` body use the OpenAI chat-completions wire format. An HTTP client pointed at `https://api.together.xyz/v1` can call it.

## Prove tool calling works {#tool-calling}

A response with text only proves the endpoint is up. A tool-calling round trip verifies the model integration: expect `tool_calls` in the response, not prose.

```bash title="curl"
curl -s https://api.together.xyz/v1/chat/completions \
  -H "Authorization: Bearer $TOGETHER_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "model": "meta-models/Muse-Glimmer-30B",
    "messages": [{"role": "user", "content": "Weather in Paris, Tokyo and Cairo?"}],
    "tools": [{"type": "function", "function": {"name": "get_weather",
      "description": "Get current weather for a city",
      "parameters": {"type": "object", "properties": {"city": {"type": "string"}},
                     "required": ["city"]}}}]
  }'
```

A working call returns three parallel `tool_calls` entries, one per city, in a single assistant turn, with reasoning available separately on the response object.

You can also drive the same prompt from [Together's Muse Glimmer playground](https://api.together.ai/playground/meta-models/Muse-Glimmer-30B).

## Behavior worth knowing {#behavior}

**Sampling.** Defaults come from the checkpoint: `temperature 0.95`, `top_p 1.0`. Greedy decoding loops on this model, so don't set `temperature` to `0`.

> [!WARNING] Never stop on the eom token
> Stop tokens: `eos_token_id = [<|end_of_text|>, <|eot|>]`. Never add `<|eom|>` to a `stop` parameter. It marks the end of a message, the turn continues after it, and stopping there reduces parallel tool calling to near zero. See [special tokens](/docs/muse-glimmer/prompting#special-tokens) for background.

**Weights.** Nothing here downloads them. For the model card or to run the same model locally, use [`meta-models/Muse-Glimmer-30B`](https://huggingface.co/meta-models/Muse-Glimmer-30B) on Hugging Face.

## What Together measured {#together-measurements}

These metrics are not on the model page. Together reported them through Mourya Vangala Srinivasa on 2026-08-10. They describe Together's serving stack rather than anything you configure.

| Metric | Value |
| --- | --- |
| TTFT p50 | 307 ms |
| Output tokens/s per request | 105 |

Together measured a dedicated 2xH100-80GB tensor-parallel replica under a sustained 0.4 QPS long-context replay: mean input 58,290 tokens (p99 approximately 127K), mean output 244 tokens, and 1-2 requests in flight. That is long-prompt agentic traffic, not a short-prompt microbenchmark. TTFT at 1K-token inputs is substantially lower.

Together also reports serving the model quantized to FP8: MLP-only blockwise e4m3, 128x128, with dynamic activations. Attention, embeddings, and the vision tower stay BF16. Together chose this configuration after checking quality against a BF16 reference on the same hardware: GPQA-Diamond 83.7 +/- 0.9 over six runs, against 83.5 on the model card. Precision is not something you select on this endpoint. The detail helps when you compare a hosted result with a local BF16 result.

## Troubleshooting {#troubleshooting}

| Symptom | Cause | Fix |
| --- | --- | --- |
| `401` on every request | `TOGETHER_API_KEY` unset, or the key is from a different account | Re-export the key from `https://api.together.xyz/settings/api-keys` and rerun the `/v1/models` check above |
| Output repeats or loops | `temperature 0` or greedy decoding | Use the checkpoint defaults (`temperature 0.95`, `top_p 1.0`) |
| Multi-tool prompts produce one call per turn instead of parallel calls | `<|eom|>` passed as a stop token, or a client that flattens `tools` into the prompt | Send `tools` as a top-level request field and leave `stop` unset |
| Long requests end at 32,768 output tokens | Together caps generation per request | Split the task; the cap guards runaway reasoning loops |
| `503 Service unavailable` minutes after provisioning a dedicated endpoint | Replica still warming; Together reports approximately 10-15 minutes for graph compilation and FP8 kernel warmup | Retry with backoff until the first `200`. Serverless is not affected |

## Support {#support}

- [Model page](https://www.together.ai/models/muse-glimmer)
- [Docs](https://docs.together.ai)
- [Pricing](https://www.together.ai/pricing)
- [Support](https://www.together.ai/support)

## Next steps

Tune your requests with the [Muse Glimmer prompting guide](/docs/muse-glimmer/prompting), or compare Together AI with the [self-hosted runtimes](/docs/muse-glimmer/deploy).
