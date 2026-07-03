Egendefinerte kommandoer lar deg spesifisere en ledetekst du vil kjøre når kommandoen utføres i TUI.

```bash frame="none"
/my-command
```

Egendefinerte kommandoer kommer i tillegg til de innebygde kommandoene som `/init`, `/undo`, `/redo`, `/share`, `/help`. [Finn ut mer](/docs/tui#commands).

---

## Lag kommandofiler

Lag nedmerkingsfiler i `commands/`-katalogen for å definere egendefinerte kommandoer.

Opprett `.opencode/commands/test.md`:

```md title=".opencode/commands/test.md"
---
description: Run tests with coverage
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---

Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

Frontmatter definerer kommandoegenskaper. Innholdet blir malen.

Bruk kommandoen ved å skrive `/` etterfulgt av kommandonavnet.

```bash frame="none"
"/test"
```

---

## Konfigurasjon

Du kan legge til egendefinerte kommandoer gjennom OpenCode-konfigurasjonen eller ved å lage markdown-filer i katalogen `commands/`.

---

### JSON

Bruk alternativet `command` i OpenCode [config](/docs/config):

```json title="opencode.jsonc" {4-12}
{
  "$schema": "https://opencode.ai/config.json",
  "command": {
    // This becomes the name of the command
    "test": {
      // This is the prompt that will be sent to the LLM
      "template": "Run the full test suite with coverage report and show any failures.\nFocus on the failing tests and suggest fixes.",
      // This is shown as the description in the TUI
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-3-5-sonnet-20241022"
    }
  }
}
```

Nå kan du kjøre denne kommandoen i TUI:

```bash frame="none"
/test
```

---

### Markdown

Du kan også definere kommandoer ved å bruke markdown-filer. Plasser dem i:

- Globalt: `~/.config/opencode/commands/`
- Per prosjekt: `.opencode/commands/`

```markdown title="~/.config/opencode/commands/test.md"
---
description: Run tests with coverage
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---

Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

Markdown-filnavnet blir kommandonavnet. For eksempel lar `test.md`
deg kjøre:

```bash frame="none"
/test
```

---

## Ledetekstkonfigurasjon

Ledetekstene for de egendefinerte kommandoene støtter flere spesielle plassholdere og syntaks.

---

### Argumenter

Send argumenter til kommandoer ved å bruke plassholderen `$ARGUMENTS`.

```md title=".opencode/commands/component.md"
---
description: Create a new component
---

Create a new React component named $ARGUMENTS with TypeScript support.
Include proper typing and basic structure.
```

Kjør kommandoen med argumenter:

```bash frame="none"
/component Button
```

Og `$ARGUMENTS` vil bli erstattet med `Button`.

Du kan også få tilgang til individuelle argumenter ved å bruke posisjonelle parametere:

- `$1` - Første argument
- `$2` - Andre argument
- `$3` - Tredje argument
- Og så videre...

For eksempel:

```md title=".opencode/commands/create-file.md"
---
description: Create a new file with content
---

Create a file named $1 in the directory $2
with the following content: $3
```

Kjør kommandoen:

```bash frame="none"
/create-file config.json src "{ \"key\": \"value\" }"
```

Dette erstatter:

- `$1` med `config.json`
- `$2` med `src`
- `$3` med `{ "key": "value" }`

---

### Shell-utdata

Bruk _!`command`_ for å injisere [bash-kommando](/docs/tui#bash-commands)-utdata i ledeteksten.

For eksempel, for å lage en egendefinert kommando som analyserer testdekning:

```md title=".opencode/commands/analyze-coverage.md"
---
description: Analyze test coverage
---

Here are the current test results:
!`npm test`

Based on these results, suggest improvements to increase coverage.
```

Eller for å se gjennom nylige endringer:

```md title=".opencode/commands/review-changes.md"
---
description: Review recent changes
---

Recent git commits:
!`git log --oneline -10`

Review these changes and suggest any improvements.
```

Kommandoer kjøres i prosjektets rotkatalog og utdataene deres blir en del av ledeteksten.

---

### Filreferanser

Inkluder filer i kommandoen din ved å bruke `@` etterfulgt av filnavnet.

```md title=".opencode/commands/review-component.md"
---
description: Review component
---

Review the component in @src/components/Button.tsx.
Check for performance issues and suggest improvements.
```

Filinnholdet blir automatisk inkludert i ledeteksten.

---

## Alternativer

La oss se på konfigurasjonsalternativene i detalj.

---

### Mal

Alternativet `template` definerer ledeteksten som vil bli sendt til LLM når kommandoen utføres.

```json title="opencode.json"
{
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report and show any failures.\nFocus on the failing tests and suggest fixes."
    }
  }
}
```

Dette er et **obligatorisk** konfigurasjonsalternativ.

---

### Beskrivelse

Bruk alternativet `description` for å gi en kort beskrivelse av hva kommandoen gjør.

```json title="opencode.json"
{
  "command": {
    "test": {
      "description": "Run tests with coverage"
    }
  }
}
```

Dette vises som beskrivelsen i TUI når du skriver inn kommandoen.

---

### Agent

Bruk `agent`-konfigurasjonen for å spesifisere hvilken [agent](/docs/agents) som skal utføre denne kommandoen.
Hvis dette er en [subagent](/docs/agents/#subagents), vil kommandoen utløse en subagent påkalling som standard.
For å deaktivere denne virkemåten, sett `subtask` til `false`.

```json title="opencode.json"
{
  "command": {
    "review": {
      "agent": "plan"
    }
  }
}
```

Denne kommandoen vil veilede deg gjennom å lage en ny agent med en tilpasset systemmelding og verktøykonfigurasjon.

---

### Underoppgave

Bruk `subtask` for å tvinge kommandoen til å utløse en [subagent](/docs/agents/#subagents) påkalling.
Dette er nyttig hvis du vil at kommandoen ikke skal forurense din primære kontekst og vil **tvinge** agenten til å fungere som en underagent,
selv om `mode` er satt til `primary` på [agent](/docs/agents) konfigurasjonen.

```json title="opencode.json"
{
  "command": {
    "analyze": {
      "subtask": true
    }
  }
}
```

Dette er et **valgfritt** konfigurasjonsalternativ.

---

### Modell

Bruk `model`-konfigurasjonen for å overstyre standardmodellen for denne kommandoen.

```json title="opencode.json"
{
  "command": {
    "analyze": {
      "model": "anthropic/claude-3-5-sonnet-20241022"
    }
  }
}
```

Dette er et **valgfritt** konfigurasjonsalternativ.

---

## Innebygd

OpenCode inkluderer flere innebygde kommandoer som `/init`, `/undo`, `/redo`, `/share`, `/help`; [finn ut mer](/docs/tui#commands).

:::note
Egendefinerte kommandoer kan overstyre innebygde kommandoer.
:::

Hvis du definerer en egendefinert kommando med samme navn, vil den overstyre den innebygde kommandoen.
