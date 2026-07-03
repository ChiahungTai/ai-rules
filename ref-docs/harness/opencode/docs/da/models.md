OpenCode bruger [AI SDK](https://ai-sdk.dev/) og [Models.dev](https://models.dev) til at understøtte **75+ LLM udbydere** og det understøtter at køre lokale modeller.

---

## Udbydere

De fleste populære udbydere er forudindlæst som standard. Hvis du har tilføjet legitimationsoplysningerne for en udbyder gennem kommandoen `/connect`, vil de være tilgængelige, når du starter OpenCode.

Få mere at vide om [providers](/docs/providers).

---

## Vælg en model

Når du har konfigureret din udbyder, kan du vælge den ønskede model ved at indtaste:

```bash frame="none"
/models
```

---

## Anbefalede modeller

Der er mange modeller derude, og der kommer nye modeller hver uge.

:::tip
Overvej at bruge en af ​​de modeller, vi anbefaler.
:::

Der er dog kun få af dem, der er gode til både at generere kode og værktøjsopkald.

Her er flere modeller, der fungerer godt med OpenCode, uden bestemt rækkefølge. (Dette er ikke en udtømmende liste og er heller ikke nødvendigvis opdateret):

- GPT 5.2
- GPT 5.1 Codex
- Claude Opus 4,5
- Claude Sonnet 4,5
- Minimax M2.1
- Gemini 3 Pro

---

## Indstil en standard

For at indstille en af ​​disse som standardmodellen kan du indstille `model`-nøglen i din
OpenCode konfig.

```json title="opencode.json" {3}
{
  "$schema": "https://opencode.ai/config.json",
  "model": "lmstudio/google/gemma-3n-e4b"
}
```

Her er det fulde ID `provider_id/model_id`. For eksempel, hvis du bruger [OpenCode Zen](/docs/zen), vil du bruge `opencode/gpt-5.1-codex` til GPT 5.1 Codex.

Hvis du har konfigureret en [custom provider](/docs/providers#custom), er `provider_id` nøglen fra `provider` delen af ​​din konfiguration, og `model_id` er nøglen fra `provider.models`.

---

## Konfiguration af modeller

Du kan konfigurere en models muligheder globalt gennem konfigurationen.

```jsonc title="opencode.jsonc" {7-12,19-24}
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "openai": {
      "models": {
        "gpt-5": {
          "options": {
            "reasoningEffort": "high",
            "textVerbosity": "low",
            "reasoningSummary": "auto",
            "include": ["reasoning.encrypted_content"],
          },
        },
      },
    },
    "anthropic": {
      "models": {
        "claude-sonnet-4-5-20250929": {
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 16000,
            },
          },
        },
      },
    },
  },
}
```

Her konfigurerer vi globale indstillinger for to indbyggede modeller: `gpt-5` når de tilgås via `openai` udbyderen og `claude-sonnet-4-20250514` når de tilgås via `anthropic` udbyderen.
Den indbyggede udbyder og modelnavne kan findes på [Models.dev](https://models.dev).

Du kan også konfigurere disse indstillinger for alle agenter, du bruger. Agentkonfigurationen tilsidesætter alle globale muligheder her. [Learn more](/docs/agents/#additional).

Du kan også definere brugerdefinerede varianter, der udvider de indbyggede. Varianter giver dig mulighed for at konfigurere forskellige indstillinger for den samme model uden at oprette duplikerede poster:

```jsonc title="opencode.jsonc" {6-21}
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "opencode": {
      "models": {
        "gpt-5": {
          "variants": {
            "high": {
              "reasoningEffort": "high",
              "textVerbosity": "low",
              "reasoningSummary": "auto",
            },
            "low": {
              "reasoningEffort": "low",
              "textVerbosity": "low",
              "reasoningSummary": "auto",
            },
          },
        },
      },
    },
  },
}
```

---

## Varianter

Mange modeller understøtter flere varianter med forskellige konfigurationer. OpenCode leveres med indbyggede standardvarianter til populære udbydere.

### Indbyggede varianter

OpenCode leveres med standardvarianter for mange udbydere:

**Anthropic**:

- `high` - Højt tænkende budget (standard)
- `max` - Maksimalt tænkebudget

**OpenAI**:

Varierer efter model, men nogenlunde:

- `none` - Ingen begrundelse
- `minimal` - Minimal ræsonnement indsats
- `low` - Lav ræsonnement indsats
- `medium` - Middel ræsonnement indsats
- `high` - Høj ræsonnement indsats
- `xhigh` - Ekstra høj ræsonnement indsats

**Google**:

- `low` - Lavere effort/token budget
- `high` - Højere effort/token budget

:::tip
Denne liste er ikke udtømmende. Mange andre udbydere har også indbyggede standardindstillinger.
:::

### Brugerdefinerede varianter

Du kan tilsidesætte eksisterende varianter eller tilføje dine egne:

```jsonc title="opencode.jsonc" {7-18}
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "openai": {
      "models": {
        "gpt-5": {
          "variants": {
            "thinking": {
              "reasoningEffort": "high",
              "textVerbosity": "low",
            },
            "fast": {
              "disabled": true,
            },
          },
        },
      },
    },
  },
}
```

### Skift varianter

Brug tastebindingen `variant_cycle` til hurtigt at skifte mellem varianter. [Learn more](/docs/keybinds).

---

## Indlæsning af modeller

Når OpenCode starter op, søger den efter modeller i følgende prioriterede rækkefølge:

1. Kommandolinjeflaget `--model` eller `-m`. Formatet er det samme som i konfigurationsfilen: `provider_id/model_id`.

2. Modellisten i OpenCode-konfigurationen.

   ```json title="opencode.json"
   {
     "$schema": "https://opencode.ai/config.json",
     "model": "anthropic/claude-sonnet-4-20250514"
   }
   ```

   Formatet her er `provider/model`.

3. Den sidst brugte model.

4. Den første model med en intern prioritet.
