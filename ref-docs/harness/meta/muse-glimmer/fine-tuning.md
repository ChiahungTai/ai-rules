---
meta:
  title: Fine-tuning
  description: Fine-tune Muse Glimmer with LoRA, QLoRA, or full-parameter supervised training for your domain.
  keywords: muse glimmer, fine-tuning, SFT, LoRA, QLoRA, training, adaptation
cms:
  alias: /model-api/docs/muse-glimmer/fine-tuning
  target: aidmc
---

# Fine-tuning

Adapt Muse Glimmer to your domain with supervised fine-tuning (SFT) on your own labeled examples. Low-rank adaptation (LoRA) is the recommended approach: it trains a small set of adapter weights while keeping the base model frozen, reducing GPU memory requirements by an order of magnitude.

Fine-tuning is the first stage of [customization](/docs/muse-glimmer/customization). For optimizing against a reward signal after SFT, see [reinforcement learning](/docs/muse-glimmer/rl).

## Choose an approach {#choose-an-approach}

<!-- TODO(validate): confirm memory/time figures against a reference Muse Glimmer 30B SFT run. The ranges below use shorter training sequences and should be treated as guidance, not guarantees. -->

| Method | Relative training cost | When to use |
| --- | --- | --- |
| LoRA | Low | Domain adaptation, style transfer, instruction tuning |
| QLoRA | Low (slower steps, less memory) | Same use cases as LoRA, with a quantized base model |
| Full fine-tune | High | Maximum quality when compute is not a constraint |

## Prepare your data {#prepare-data}

Format your training data as JSONL with the chat format Muse Glimmer expects:

```json title="JSON"
{"messages": [{"role": "system", "content": "You are a medical assistant."}, {"role": "user", "content": "What are the symptoms of type 2 diabetes?"}, {"role": "assistant", "content": "Common symptoms include increased thirst, frequent urination, fatigue, and blurred vision."}]}
{"messages": [{"role": "system", "content": "You are a medical assistant."}, {"role": "user", "content": "How is hypertension diagnosed?"}, {"role": "assistant", "content": "Hypertension is diagnosed by measuring blood pressure. A reading consistently at or above 130/80 mmHg indicates hypertension."}]}
```

- One conversation per line.
- Include a system prompt in every example if you want the model to follow a consistent persona.
- Aim for at least a few hundred (roughly 500+) high-quality examples for meaningful adaptation; several thousand (5,000–10,000+) for strong domain performance. Quality and consistency matter more than raw count.

> [!NOTE] Train on reasoning traces
> Muse Glimmer is a reasoning model. If you want it to keep reasoning on your task, include the reasoning trace in your training targets (via `reasoning_content`); if you fine-tune only on final answers, you may suppress the model's chain-of-thought. Match your training data to the behavior you want at inference.

## LoRA fine-tuning {#lora}

<!-- TODO(validate): confirm target_modules and hyperparameters against the Muse Glimmer architecture (MuseGlimmerForCausalLM) before publishing. -->

```python title="Python"
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer

model_name = "meta-models/Muse-Glimmer-30B"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)

training_args = TrainingArguments(
    output_dir="./muse-glimmer-lora",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    bf16=True,
    logging_steps=10,
    save_strategy="epoch",
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,  # your loaded dataset
    processing_class=tokenizer,
)

trainer.train()
trainer.save_model("./muse-glimmer-lora")
```

## QLoRA fine-tuning {#qlora}

QLoRA loads the base model in 4-bit precision with `bitsandbytes`, then trains LoRA adapters on top. This cuts GPU memory requirements substantially compared to standard LoRA.

```python title="Python"
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
import torch

model_name = "meta-models/Muse-Glimmer-30B"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    model_name, quantization_config=bnb_config, device_map="auto"
)
model = prepare_model_for_kbit_training(model)
tokenizer = AutoTokenizer.from_pretrained(model_name)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)

trainer = SFTTrainer(
    model=model,
    args=TrainingArguments(
        output_dir="./muse-glimmer-qlora",
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        learning_rate=2e-4,
        bf16=True,
        logging_steps=10,
        save_strategy="epoch",
    ),
    train_dataset=train_dataset,
    processing_class=tokenizer,
)
trainer.train()
trainer.save_model("./muse-glimmer-qlora")
```

## Hyperparameter guidance {#hyperparameters}

<!-- TODO(validate): confirm ranges against a reference Muse Glimmer SFT run. -->

| Parameter | Recommended range | Notes |
| --- | --- | --- |
| Learning rate | 1e-4 – 3e-4 (LoRA/QLoRA) | Lower for larger datasets; full fine-tunes use ~1e-5 |
| LoRA rank (`r`) | 8 – 32 | Higher rank = more capacity, more memory |
| LoRA alpha | 2× rank | Standard scaling |
| Batch size | 4 – 16 (effective) | Use gradient accumulation to reach this |
| Epochs | 2 – 5 | Watch for overfitting on small datasets |
| Model context window | 128K by default | The model supports longer contexts; this describes model capacity, not a recommended per-example training length |
| Training sequence length | Dataset- and hardware-dependent | Start with shorter sequences to reduce memory, and increase only after validating quality and hardware headroom |


## Evaluate after fine-tuning {#evaluate}

Compare your fine-tuned model against the base model on a held-out test set before deploying. Track both your task metric and a general-capability benchmark so you catch regressions from over-fitting:

Load the base model with the adapter you just trained — that is what you have at
this point. Swap `./muse-glimmer-lora` for `./muse-glimmer-qlora` if you took the
QLoRA path, or point `from_pretrained` at the merged directory once you have run
[Merge adapters](#merge-adapters) below.

```python title="Python"
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base_model = AutoModelForCausalLM.from_pretrained(
    "meta-models/Muse-Glimmer-30B",
    torch_dtype="auto",
    device_map="auto",
)
model = PeftModel.from_pretrained(base_model, "./muse-glimmer-lora")
tokenizer = AutoTokenizer.from_pretrained("meta-models/Muse-Glimmer-30B")

correct = 0
for example in test_set:  # each has .messages (prompt) and .expected
    prompt = tokenizer.apply_chat_template(example.messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    output = model.generate(**inputs, max_new_tokens=512, do_sample=False)
    answer = tokenizer.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    correct += int(example.expected in answer)

print(f"accuracy: {correct / len(test_set):.1%}")
```

If your fine-tune improves the task metric but drops general capability, reduce epochs, lower the learning rate, or add more diverse data.

## Merge adapters {#merge-adapters}

Merge LoRA adapters back into the base model for deployment without the PEFT library:

```python title="Python"
from peft import PeftModel
from transformers import AutoModelForCausalLM

base_model = AutoModelForCausalLM.from_pretrained(
    "meta-models/Muse-Glimmer-30B",
    torch_dtype="auto",
    device_map="auto",
)
model = PeftModel.from_pretrained(base_model, "./muse-glimmer-lora")
merged = model.merge_and_unload()
merged.save_pretrained("./muse-glimmer-30b-merged")
```

The merged model can be served with any runtime (vLLM, llama.cpp) without adapter overhead.

## Next steps

Optimize your fine-tuned model further with [reinforcement learning](/docs/muse-glimmer/rl), then [deploy it](/docs/muse-glimmer/deploy) with vLLM, llama.cpp, or ExecuTorch. To convert it for local inference, see [quantization](/docs/muse-glimmer/quantization).
