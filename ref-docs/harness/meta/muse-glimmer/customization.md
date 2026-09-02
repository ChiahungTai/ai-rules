---
meta:
  title: Customization
  description: Adapt Muse Glimmer to your domain with supervised fine-tuning (SFT) and reinforcement learning (RL).
  keywords: muse glimmer, customization, fine-tuning, SFT, RL, reinforcement learning, post-training
cms:
  alias: /model-api/docs/muse-glimmer/customization
  target: aidmc
---

# Customization

Adapt Muse Glimmer to your domain in two stages, mirroring how the released model was post-trained: **supervised fine-tuning (SFT)** teaches the model your task format and style from labeled examples, and **reinforcement learning (RL)** optimizes behavior against a reward signal — preference data or a programmatic reward — where labeled targets alone aren't enough.

Most projects start (and often stop) at SFT. Use RL when you need to optimize an outcome you can score but can't fully demonstrate: preference alignment, tool-use success, or reward-shaped agentic behavior.

| Stage | What it does | When to use | Data you need |
| --- | --- | --- | --- |
| [Fine-tuning (SFT)](/docs/muse-glimmer/fine-tuning) | Trains on labeled input→output examples (LoRA, QLoRA, or full) | Domain adaptation, style, format, instruction following | Prompt/response pairs in chat format |
| [Reinforcement learning](/docs/muse-glimmer/rl) | Optimizes against a reward signal (preference or programmatic) | Preference alignment, tool-use success, agentic behavior | A reward model, preference pairs, or a verifiable reward |

> [!NOTE] SFT first, then RL
> SFT and RL work together. The standard recipe layers them — supervised fine-tuning first for well-formatted outputs, then reinforcement learning on that checkpoint, where RL is far more stable.

<tile-group col="2">
<tile color="blue" icon="pencil" href="/docs/muse-glimmer/fine-tuning" title="Fine-tuning (SFT)">Adapt Muse Glimmer to your domain with LoRA, QLoRA, or full fine-tuning.</tile>
<tile color="purple" icon="robot-head" href="/docs/muse-glimmer/rl" title="Reinforcement learning">Optimize behavior against preference data or a programmatic reward.</tile>
</tile-group>

## Next steps

Prepare your data and run your first [supervised fine-tune](/docs/muse-glimmer/fine-tuning). When you have an SFT checkpoint that behaves well, layer on [reinforcement learning](/docs/muse-glimmer/rl). Deploy the result with any [runtime](/docs/muse-glimmer/deploy).
