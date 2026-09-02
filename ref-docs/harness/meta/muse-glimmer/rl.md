---
meta:
  title: Reinforcement learning
  description: Optimize Muse Glimmer against a reward signal with preference optimization (DPO) or online RL (GRPO/PPO).
  keywords: muse glimmer, reinforcement learning, RL, DPO, GRPO, PPO, preference optimization, RLHF
cms:
  alias: /model-api/docs/muse-glimmer/rl
  target: aidmc
---

# Reinforcement learning

Reinforcement learning optimizes Muse Glimmer against a **reward signal** rather than fixed target outputs. Use it when you can *score* an output but can't fully *demonstrate* it: aligning to human preferences, rewarding successful tool calls, or shaping multi-step agentic behavior.

Always start RL from a [supervised fine-tuned](/docs/muse-glimmer/fine-tuning) checkpoint. RL is much more stable when the policy already produces well-formatted, on-task outputs. RL refines existing behavior; it won't teach the output format from scratch.

## Choose a method {#choose-a-method}

| Method | Reward source | Cost | When to use |
| --- | --- | --- | --- |
| DPO (Direct Preference Optimization) | Preference pairs (chosen vs. rejected) | Low — offline, no reward model, no sampling | You have pairwise preference data and want alignment without standing up a reward model |
| GRPO (Group Relative Policy Optimization) | A programmatic or model-based reward | Higher — online sampling during training | You have a verifiable reward (unit tests pass, answer matches, tool call succeeds) |
| PPO | A trained reward model | Highest — reward model + online sampling | Classic RLHF when you have (or train) a scalar reward model |

For most teams, **DPO is the fastest path**: it needs only preference pairs and trains offline like SFT. Use **GRPO** when your task has a checkable, programmatic reward (common for reasoning and tool-use). **PPO** is the general RLHF workhorse but requires the most infrastructure.

## Preference optimization with DPO {#dpo}

DPO trains directly on preference pairs — no separate reward model, no online sampling. Format your data as a prompt with a `chosen` and a `rejected` completion:

```json title="JSON"
{"prompt": [{"role": "user", "content": "Explain a mutex to a new engineer."}], "chosen": [{"role": "assistant", "content": "A mutex is a lock that lets only one thread into a critical section at a time..."}], "rejected": [{"role": "assistant", "content": "A mutex is when the CPU mutexes the threads."}]}
```

<!-- TODO(validate): confirm hyperparameters (beta, learning rate) against the Muse Glimmer RL recipe once published. -->

```python title="Python"
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer

model_name = "meta-models/Muse-Glimmer-30B"

model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)

config = DPOConfig(
    output_dir="./muse-glimmer-dpo",
    beta=0.1,                 # KL penalty strength; lower = stays closer to the reference
    learning_rate=5e-7,       # DPO uses a much lower LR than SFT
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=1,
    bf16=True,
    logging_steps=10,
)

trainer = DPOTrainer(
    model=model,
    args=config,
    train_dataset=preference_dataset,  # your loaded dataset with prompt/chosen/rejected
    processing_class=tokenizer,
)

trainer.train()
trainer.save_model("./muse-glimmer-dpo")
```

DPO keeps a frozen reference copy of the model and penalizes the policy for drifting too far from it (the `beta` term). Start with `beta=0.1` and a learning rate around `5e-7` — RL-family objectives are far more sensitive to learning rate than SFT.

## Online RL with a programmatic reward (GRPO) {#grpo}

When your task has a reward you can *compute* — code that passes tests, a math answer that matches, a tool call that succeeds — GRPO optimizes against it directly. GRPO samples a group of completions per prompt and reinforces the ones that score above the group average, which removes the need for a separate value/critic network.

```python title="Python"
from trl import GRPOConfig, GRPOTrainer

def reward_fn(completions, **kwargs):
    # Return one scalar reward per completion. Example: reward a parseable final answer.
    # Replace this example with your task's verifiable reward.
    return [1.0 if "<answer>" in c else 0.0 for c in completions]

config = GRPOConfig(
    output_dir="./muse-glimmer-grpo",
    learning_rate=1e-6,
    per_device_train_batch_size=1,
    num_generations=8,         # group size sampled per prompt
    max_completion_length=4096,  # allow room for Muse Glimmer's long reasoning traces
    bf16=True,
)

trainer = GRPOTrainer(
    model="meta-models/Muse-Glimmer-30B",  # Start from your SFT checkpoint.
    reward_funcs=reward_fn,
    args=config,
    train_dataset=prompt_dataset,  # prompts only — completions are sampled online
)

trainer.train()
```

> [!NOTE] Size completion length for reasoning
> Muse Glimmer generates long chain-of-thought before its final answer. Set `max_completion_length` high enough to fit the reasoning trace (Muse Glimmer's default context window is 128K tokens, with longer contexts supported), and design rewards that score the **final answer**, not the reasoning tokens, unless you specifically want to shape the reasoning.

## Hyperparameter guidance {#hyperparameters}

<!-- TODO(validate): fill in ranges confirmed against the Muse Glimmer RL recipe. -->

| Parameter | DPO | GRPO / PPO | Notes |
| --- | --- | --- | --- |
| Learning rate | 1e-7 – 1e-6 | 1e-6 – 3e-6 | Orders of magnitude lower than SFT |
| KL / `beta` | 0.1 – 0.5 | KL coeff 0.01 – 0.1 | Higher keeps the policy closer to the reference |
| Epochs / steps | 1 – 2 epochs | Step-based | RL overfits fast; watch reward and a held-out eval |
| Group size (`num_generations`) | — | 4 – 16 | Larger groups give a lower-variance advantage estimate |

## Guard against reward hacking {#reward-hacking}

RL optimizes exactly what you reward — including unintended shortcuts. Protect against drift:

- **Keep a KL penalty** to the reference (SFT) model so the policy can't collapse into degenerate outputs that game the reward.
- **Hold out an eval set** the reward never sees, and track general capability (for example [GPQA](/docs/muse-glimmer) or your domain benchmark) alongside reward. If reward climbs while eval quality drops, the model is hacking the reward.
- **Inspect samples**, not just scalars. Read generations at each checkpoint; reward hacking is usually obvious to a human before it shows up in aggregate metrics.

## Evaluate and deploy {#evaluate}

Compare the RL checkpoint against both the base and the SFT checkpoint on a held-out test set before shipping. When it wins, [merge any adapters](/docs/muse-glimmer/fine-tuning#merge-adapters) and serve it with any [runtime](/docs/muse-glimmer/deploy).

## Next steps

If you haven't run [supervised fine-tuning](/docs/muse-glimmer/fine-tuning) yet, start there. RL builds on an SFT checkpoint. Once your customized model is ready, [deploy it](/docs/muse-glimmer/deploy) with vLLM, llama.cpp, or ExecuTorch.
