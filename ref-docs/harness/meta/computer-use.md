---
meta:
  title: Build a computer-use agent
  description: Drive Muse Spark as a computer-use agent with a developer-defined computer tool — screenshots in, normalized actions out, executed in your own harness.
  keywords: computer use, CUA, computer-use agent, browser automation, GUI automation, screenshots, function tool, Responses API
cms:
  alias: /model-api/docs/computer-use
  target: aidmc
---

# Build a computer-use agent

Give [Muse Spark](/docs/models#muse-spark) a screen and let it drive. A computer-use agent (CUA) looks at a screenshot, decides where to click and what to type, and works a browser or desktop toward a goal one action at a time. You expose the environment as a developer-defined [function tool](/docs/tool-calling): the model proposes actions, your harness executes them, and you hand back the next screenshot.

This guide shows the loop, the tool contract, and the harness responsibilities that make CUA reliable — coordinates, batching, context budgeting, and knowing when to stop.

## How the loop works {#how-it-works}

Computer use runs as a tight observe-act loop:

1. **Capture** the current browser or screen as a screenshot.
2. **Send** the task, the latest screenshot, and recent history to Muse Spark over the [Responses API](/docs/protocols/responses).
3. **Receive** one or more computer actions as a tool call.
4. **Execute** the actions in your environment.
5. **Repeat** from step 1 until the task is done or infeasible.

Muse Spark decides what to do next; your application owns everything else — the environment, action execution, screenshot capture, validation, logging, and recovery. The model never needs to know your automation library or VM internals. It sees a small action vocabulary and the current screen.

## Define the computer tool {#computer-tool}

Expose computer control as a function tool that accepts a batch of actions, executes them in order, and returns the resulting screenshot. Use the flat tool schema of the Responses API:

```json title="JSON"
{
  "type": "function",
  "name": "computer.computer",
  "description": "Execute one or more computer actions in the browser or desktop environment.",
  "parameters": {
    "type": "object",
    "properties": {
      "actions": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "enum": [
                "key", "type", "mouse_move", "left_click", "left_click_drag",
                "right_click", "middle_click", "double_click", "triple_click",
                "left_press", "scroll", "hold_key", "release_key",
                "left_mouse_down", "left_mouse_up", "wait"
              ]
            },
            "coordinate": {
              "type": "array",
              "items": {"type": "integer"},
              "minItems": 2,
              "maxItems": 2,
              "description": "[x, y] on a normalized 0-1000 grid."
            },
            "start_coordinate": {
              "type": "array",
              "items": {"type": "integer"},
              "minItems": 2,
              "maxItems": 2,
              "description": "[x, y] start point for drag actions."
            },
            "text": {
              "type": "string",
              "description": "Text to type, a key combination, or a modifier for click/scroll."
            },
            "scroll_direction": {"type": "string", "enum": ["up", "down", "left", "right"]},
            "scroll_amount": {"type": "integer"},
            "duration": {"type": "number"}
          },
          "required": ["action"]
        }
      }
    },
    "required": ["actions"],
    "additionalProperties": false
  }
}
```

Pair it with a separate `computer.stop` tool for terminal states, so ending the session is an explicit decision the model makes rather than a guess your parser has to make:

```json title="JSON"
{
  "type": "function",
  "name": "computer.stop",
  "description": "Stop the session and submit the final answer, or explain why the task is infeasible.",
  "parameters": {
    "type": "object",
    "properties": {
      "answer": {
        "type": "string",
        "description": "A short description of the completed task, or why it cannot be completed. Include the word 'infeasible' if the task cannot be done."
      }
    },
    "required": ["answer"],
    "additionalProperties": false
  }
}
```

Keep the action vocabulary small and stable. The tool hides your executor: internally you map each action to your automation library (such as pyautogui, Playwright, or a VM driver), but the model only sees these names.

## Use normalized coordinates {#coordinates}

Have the model output every point on a normalized **0–1000 grid**: `(0, 0)` is the top-left of the screenshot, `(1000, 1000)` is the bottom-right. This is the same coordinate space Muse Spark uses for [perception grounding](/docs/image-understanding), so the model already reasons about screens this way, and the contract stays stable across screenshot sizes and display resolutions.

Your executor maps normalized coordinates back to pixels against the exact image the model saw:

```python title="Python"
def to_pixels(x_norm, y_norm, screen_width, screen_height):
    x = round(x_norm * screen_width / 1000)
    y = round(y_norm * screen_height / 1000)
    # The model can emit slightly out-of-range values at element edges.
    x = max(0, min(x, screen_width - 1))
    y = max(0, min(y, screen_height - 1))
    return x, y
```

Keep the coordinate basis consistent across a trajectory. The screenshot you send and the screen your executor acts on must stay the same size. For browser use, map to the viewport that produced the screenshot, not the full page. Switching from viewport screenshots to full-page screenshots mid-task makes earlier coordinates misleading.

## Run the loop {#agent-loop}

Drive the loop over the Responses API. Each turn, the model returns a `function_call`; you execute it, then send back a `function_call_output` (the execution status) plus a fresh screenshot as an `input_image` in a `user` message. Chain turns with `previous_response_id` so the server keeps conversation state:

```python title="Python"
import base64
import json
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)

def screenshot_data_url(png_bytes: bytes) -> str:
    b64 = base64.b64encode(png_bytes).decode()
    return f"data:image/png;base64,{b64}"

def run(task: str, executor, tools, system_prompt: str, max_steps: int = 50):
    png, w, h = executor.screenshot()
    response = client.responses.create(
        model="muse-spark-1.1",
        instructions=system_prompt,
        parallel_tool_calls=False,
        tools=tools,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": task},
                {"type": "input_image", "image_url": screenshot_data_url(png)},
            ],
        }],
    )

    for _ in range(max_steps):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            break

        call = calls[0]
        args = json.loads(call.arguments)

        if call.name == "computer.stop":
            return args["answer"]

        status = executor.execute(args["actions"])   # runs the batch, returns per-action status
        png, w, h = executor.screenshot()

        response = client.responses.create(
            model="muse-spark-1.1",
            previous_response_id=response.id,
            parallel_tool_calls=False,
            tools=tools,
            input=[
                {"type": "function_call_output", "call_id": call.call_id, "output": json.dumps(status)},
                {"role": "user", "content": [
                    {"type": "input_image", "image_url": screenshot_data_url(png)},
                ]},
            ],
        )

    return "stopped: step budget reached"
```

Two settings matter for correctness:

- **`parallel_tool_calls=False`**: the computer tool owns batching internally, so a single tool call per turn keeps UI ordering unambiguous. See [tool calling](/docs/tool-calling).
- **`previous_response_id`**: chains each turn to the last response so you don't resend the whole trajectory. Muse Spark's reasoning carries across turns automatically on this path.

> [!NOTE] tool_choice must stay auto
> `tool_choice` defaults to `"auto"`, which is the only supported value. Let the model decide when to call the `computer.computer` tool versus the `computer.stop` tool; don't try to force a specific tool.

## Manage conversation state {#state}

You have two ways to carry history, and they trade off control against bookkeeping:

- **Server-managed state**: pass `previous_response_id` and send only the new `function_call_output` and latest screenshot each turn (as in the loop above). The server holds the trajectory. This is the simplest path and keeps reasoning continuity for free.
- **Stateless replay**: set `store: false` and keep the trajectory on the client — prior messages, tool calls, tool outputs, and recent screenshots. Request encrypted reasoning with `include: ["reasoning.encrypted_content"]` and replay the returned `reasoning` items on later turns so the model retains its own thinking. See [reasoning replay](/docs/reasoning#multi-turn).

Reach for server-managed state when you want less client-side history handling. Reach for stateless replay when reproducibility and local control matter — for example, when you log and re-run trajectories offline.

## Batch actions {#batching}

Muse Spark can return several actions in one tool call. Batching cuts round trips for sequences that don't depend on intermediate feedback, such as click, type, then press Enter:

```json title="JSON"
{
  "actions": [
    {"action": "left_click", "coordinate": [412, 315]},
    {"action": "type", "text": "quarterly revenue"},
    {"action": "key", "text": "enter"}
  ]
}
```

Keep batches short and bounded. Two to five actions is a good default; treat a higher cap as a guardrail, not a target. Your executor should:

- **Run actions in order** and capture one fresh screenshot after the batch finishes.
- **Stop early** if an action fails, the page navigates unexpectedly, a modal appears, or the screen changes in a way that invalidates later actions.
- **Return per-action status** so the model can recover on the next turn.
- **Insert a short settle delay** when a mouse action is immediately followed by keyboard input, so typing doesn't land before focus settles.

Don't batch across a step that depends on the previous result — clicking a search result after submitting a query, for example. Execute the query, let the page settle, send a new screenshot, and let the model choose the next action from what it sees.

## Validate tool arguments {#validation}

Treat tool arguments as untrusted input. Decode them, check the shape, and return a recoverable tool error with a fresh screenshot instead of crashing the run — a returned error gives the model a chance to correct its next action.

- Require a JSON object with a non-empty `actions` list.
- Validate per-action required fields: coordinates, text, scroll direction, duration.
- Reject negative wait durations and enforce your maximum batch size.
- Repair only safe, common formatting defects; reject anything ambiguous.

Reliable input handling covers more than clicks. Normalize key aliases before execution, treat key combinations as combined press-and-release sequences, type plain ASCII directly, and use clipboard paste for Unicode or complex text. Release mouse modifiers in reverse order once the intended action completes.

## Keep the context bounded {#context}

Long trajectories grow fast: every step can add a tool call, a tool output, reasoning state, and a new screenshot, and screenshots dominate the token count. Two levers keep runs inside the 1,048,576-token context window.

**Truncate old screenshots.** Keep recent visual context and drop older tool-output screenshots in chunks, leaving the text history, tool-call records, and the initial task screenshot intact. When you remove a screenshot, leave a marker on its tool output so the model knows one existed:

```text
[Screenshot has been truncated to save context]
```

Remove in chunks rather than one screenshot per turn. A chunked policy — for example, keep the 10 most recent screenshots and trim the oldest batch once the history grows past ~30 — keeps the replayed prompt prefix stable for many turns, which helps prompt-cache reuse. Trimming one screenshot every turn changes the prefix on every request and defeats caching.

**Budget output tokens.** Count input tokens before generating with [`POST /v1/responses/input_tokens`](/docs/api-reference/responses), then set `max_output_tokens` to leave margin inside the context window while keeping enough room for the model to reason and produce a tool call. Trim old screenshots before you drop recent action history, and retry transient API failures with exponential backoff.

## Handle done and infeasible {#terminal}

The model ends a session by calling the `computer.stop` tool. Your harness captures the final screenshot, saves the trajectory, and treats the stop as terminal.

**Done.** The model should stop only when the goal is visibly complete on screen or the required answer has been produced. Don't accept a "done" that follows an action triggering async work unless the resulting UI confirms it.

```json title="JSON"
{"answer": "Done: the spreadsheet cell is updated and the new value is visible on screen."}
```

**Infeasible.** Let the model give up cleanly when the task can't be completed from the available UI. This prevents loops where the agent keeps clicking after it's blocked. Use a narrow, explicit signal: the `computer.stop` answer must contain the word `infeasible`. Generic phrases such as "not supported" or "cannot be done" are useful reasoning but shouldn't count as terminal on their own.

```json title="JSON"
{"answer": "infeasible: the task requires signing in, and the current page is a login screen with no credentials available."}
```

Common infeasible conditions:

- A required app, page, file, account, or permission is unavailable.
- The task needs credentials, payment, two-factor authentication, or private data the harness can't supply.
- The UI is broken, blocked by an unsupported modal, or in a language or configuration that prevents reliable completion.
- The goal is underspecified and the model can't choose among valid targets.
- The model has retried a reasonable recovery path and sees no progress.

## Set a strict system prompt {#system-prompt}

The system prompt is where you lock in the coordinate convention and the rules for batching, waiting, finishing, and declaring infeasible. Pass it as `instructions` on the Responses API:

```text title="System prompt"
You are a computer-use agent operating a browser or desktop environment. You receive
screenshots and must choose the next action or actions.

Use normalized coordinates from 0 to 1000 for every point. (0, 0) is the top-left of the
screenshot and (1000, 1000) is the bottom-right. The executor maps these to pixels.

Return a short batch of actions only when they do not depend on intermediate visual
feedback, such as click, type, and keypress. Do not batch across page loads, searches,
modal transitions, or any step where the next action depends on a new screenshot.

Use the computer tool with these actions: key, type, mouse_move, left_click,
left_click_drag, right_click, middle_click, double_click, triple_click, left_press, scroll,
hold_key, release_key, left_mouse_down, left_mouse_up, wait. Use wait when the page is
loading or an action needs time to take effect.

Call the stop tool only when the task is complete or infeasible. Use the word "infeasible"
when the task cannot be completed because of missing permissions, credentials, unavailable
UI, ambiguity, or repeated lack of progress. Include a concise reason.

Do not guess hidden UI state and do not claim completion unless the screenshot supports it.
If a target is not visible, scroll or request a new screenshot before clicking. Before
stopping, verify the visible result and save any modified document when the task requires it.
```

## Next steps

Now that the loop is running, tighten the pieces that make it robust:

- Work through the [Cookbook](/docs/cookbook) for end-to-end agentic recipes you can adapt into your own harness.
- Wire richer environment control through [tool calling](/docs/tool-calling) and combine the computer tool with your own helpers.
- Carry the model's reasoning across long sessions with the [Responses API](/docs/protocols/responses) and [reasoning replay](/docs/reasoning).
- Feed high-quality screenshots by matching your capture to Muse Spark's [image understanding](/docs/image-understanding) and grounding behavior.
