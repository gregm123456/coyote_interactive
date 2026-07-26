# COYOTE AX650 SUPPORT PLAN

## Objective
Add a third LLM provider option, `ax650`, to `ax650_raspberry_pi_services/coyote_interactive`.

Current options are `azure` and `ollama`. New option must integrate with this repo's local AX650 deployment behavior:
- Generation calls use the Ollama-compatible endpoint on `:11434`.
- Runtime reset/control calls use AX650 runtime endpoints on `:8000`.
- AX650 runtime holds conversation history in memory.

## Non-Negotiable Behavioral Requirements
1. Add `ax650` as a valid `LLM` option.
2. For `ax650`, do NOT send full conversation transcript/messages array on each turn.
3. For `ax650`, send only the latest prompt (newest user input for the current turn).
4. AX650 needs system prompt set at runtime reset.
5. On coyote "full reset" (BOOM archive flow), coyote must also:
   - send AX650 soft stop/reset
   - reassert `SYSTEM_MESSAGE_TEXT`
6. On coyote startup (when `LLM == "ax650"`), perform AX650 reset + system prompt assertion before interactions.
7. Keep existing local JSON conversation logging and archive behavior for observability/debugging.

## Confirmed Integration Contract

### Generation Path (AX650)
- Endpoint: `http://localhost:11434/api/generate`
- Provider mode in coyote: `LLM = "ax650"`
- Model example: `qwen3-ax650`
- Request pattern: single latest prompt, non-streaming

Example request:
```json
{
  "model": "qwen3-ax650",
  "prompt": "<latest prompt only>",
  "stream": false
}
```

Expected response (Ollama-compatible shape):
```json
{
  "response": "..."
}
```

### Reset/Control Path (AX650 Runtime)
- Stop endpoint: `http://127.0.0.1:8000/api/stop`
- Reset endpoint: `http://127.0.0.1:8000/api/reset`

Reset payload must include system prompt:
```json
{
  "system_prompt": "<config.SYSTEM_MESSAGE_TEXT>"
}
```

Expected sequence:
1. `GET /api/stop`
2. `POST /api/reset` with `system_prompt`

## Files to Modify

### 1) `ax650_raspberry_pi_services/coyote_interactive/config_secrets.example.py`
Add AX650 config entries so local `config_secrets.py` can define them:
- `AX650_GENERATE_ENDPOINT` (default `http://localhost:11434/api/generate`)
- `AX650_RUNTIME_STOP_ENDPOINT` (default `http://127.0.0.1:8000/api/stop`)
- `AX650_RUNTIME_RESET_ENDPOINT` (default `http://127.0.0.1:8000/api/reset`)
- `AX650_MODEL` (default `qwen3-ax650`)
- `AX650_TIMEOUT_SECONDS` (reasonable default, e.g. `30`)
- Optional generation tuning keys if needed by implementation.

### 2) `ax650_raspberry_pi_services/coyote_interactive/config.py`
Update comments/docs around `LLM` to include `ax650`:
- Current comment implies `azure or ollama`.
- Must explicitly mention `azure`, `ollama`, and `ax650`.
- Do not force default switch unless requested; only add support cleanly.

### 3) `ax650_raspberry_pi_services/coyote_interactive/llm_chat_completion.py`
Add AX650 provider implementation and dispatcher path.

Required additions:
1. `chat_completion_ax650(conversation_file)`
2. helper to extract latest user prompt from `conversation_file`
3. robust request/response error handling
4. dispatcher branch:
   - `elif config.LLM == "ax650": return chat_completion_ax650(conversation_file)`

Implementation rules:
- Read local conversation JSON, but AX650 request must use only latest `role == "user"` content.
- Do not send full `messages` to AX650 generation endpoint.
- Parse Ollama-style `response` field first.
- If malformed or unavailable response, return safe fallback string and log error.
- Add timeout on HTTP calls.

Suggested extraction helper behavior:
- Walk conversation list from end to start.
- Return first user message content found.
- If no user message exists, return a safe fallback prompt (or raise controlled error).

### 4) `ax650_raspberry_pi_services/coyote_interactive/coyote.py`
Wire AX650 reset lifecycle hooks.

Required changes:
1. On startup path in `main()` (or before entering active interaction loop), when `config.LLM == "ax650"`:
   - call AX650 soft stop/reset sequence
   - send `SYSTEM_MESSAGE_TEXT`
2. In BOOM path (`sleep mode` + both buttons pressed):
   - keep `archive_conversation(config)` behavior as-is
   - then trigger AX650 stop/reset + system prompt reassertion when `LLM == "ax650"`

Design guidance:
- Keep reset helper in one place (either in `llm_chat_completion.py` or a small shared module) to avoid duplicated HTTP logic.
- BOOM should still complete even if AX650 reset fails; print clear error and continue.

### 5) Documentation Updates
Update:
- `ax650_raspberry_pi_services/coyote_interactive/README.md`
- `ax650_raspberry_pi_services/coyote_interactive/INSTALL.md`
- `ax650_raspberry_pi_services/coyote_interactive/TROUBLESHOOTING.md`

Docs must state:
1. New provider option: `ax650`
2. AX650 uses stateful runtime memory
3. Coyote sends only latest prompt for AX650 turns
4. Startup + BOOM trigger runtime reset with system prompt
5. Required local config keys and defaults
6. Quick diagnostic curl commands for `:11434` and `:8000`

## Existing Flows That Should Stay Mostly Unchanged
- `comment_on_television.py` prompt creation and conversation appends
- `talk_with_person.py` prompt creation and conversation appends
- `conversation_manager.py` setup/archive mechanics

These remain provider-agnostic. AX650 behavior difference belongs in provider adapter + reset hook plumbing.

## Detailed Implementation Notes

### A) Provider Adapter Pattern
Current pattern is central dispatch in `llm_chat_completion()`.
Keep this pattern. Add AX650 branch only.

### B) Local Conversation vs AX650 Runtime State
There are two parallel states after this change:
1. Local file state (`conversation.json`) for logs/history/archive
2. AX650 runtime in-memory state for active chat context

For AX650 requests:
- local file can keep full history
- outbound generation request must include latest prompt only

### C) Reset Semantics
Reset means:
1. stop current runtime flow
2. reset runtime with `system_prompt = SYSTEM_MESSAGE_TEXT`

Triggers:
- startup when provider is AX650
- BOOM full reset

### D) Failure Handling
If AX650 endpoints fail:
- log clear message with endpoint + exception
- return a safe spoken fallback (do not crash event loop)
- do not break archive flow

## Suggested Pseudocode

### AX650 generation in `llm_chat_completion.py`
```python
def _latest_user_prompt(messages):
	for msg in reversed(messages):
		if msg.get("role") == "user":
			content = (msg.get("content") or "").strip()
			if content:
				return content
	return None


def chat_completion_ax650(conversation_file):
	messages = load_json(conversation_file)
	prompt = _latest_user_prompt(messages)
	if not prompt:
		return "Sorry, I did not catch that."

	payload = {
		"model": config.AX650_MODEL,
		"prompt": prompt,
		"stream": False,
	}

	resp = requests.post(
		config.AX650_GENERATE_ENDPOINT,
		json=payload,
		timeout=config.AX650_TIMEOUT_SECONDS,
	)
	resp.raise_for_status()
	body = resp.json()
	text = body.get("response")
	if not text:
		return "Sorry, I had trouble generating a response."
	return text
```

### AX650 reset helper
```python
def ax650_soft_reset_and_reassert_prompt():
	requests.get(config.AX650_RUNTIME_STOP_ENDPOINT, timeout=config.AX650_TIMEOUT_SECONDS)
	requests.post(
		config.AX650_RUNTIME_RESET_ENDPOINT,
		json={"system_prompt": config.SYSTEM_MESSAGE_TEXT},
		timeout=config.AX650_TIMEOUT_SECONDS,
	)
```

## Test Plan

### Unit Tests (required)
Add tests around provider dispatch and AX650 request semantics (mock `requests`):
1. `LLM == "ax650"` routes to AX650 handler.
2. AX650 payload uses only latest user prompt.
3. AX650 payload does not include full `messages` array.
4. AX650 response parsing reads `response` field.
5. HTTP error path returns safe fallback string.
6. JSON parse/missing-field path returns safe fallback string.
7. Reset helper sends stop then reset with `SYSTEM_MESSAGE_TEXT`.

### Manual Smoke Tests on Device (required)
1. Configure `LLM = "ax650"` and AX650 endpoints.
2. Start coyote; verify startup reset call occurs.
3. Trigger TV interaction; verify valid spoken response.
4. Trigger person interaction; verify continuity.
5. Trigger BOOM in sleep mode; verify:
   - conversation archive file created
   - AX650 reset calls sent
   - next interaction starts fresh persona/state
6. Validate no crashes when runtime endpoints are temporarily unavailable.

## Acceptance Criteria (Definition of Done)
1. `LLM = "ax650"` works end-to-end in coyote_interactive.
2. AX650 generation uses `:11434/api/generate` with latest prompt only.
3. AX650 reset uses `:8000/api/stop` and `:8000/api/reset` with `SYSTEM_MESSAGE_TEXT`.
4. Startup and BOOM both perform AX650 reset + prompt assertion.
5. Existing `azure` and `ollama` paths still function unchanged.
6. Local conversation logs and archive files remain intact.
7. Docs updated with setup, behavior, and troubleshooting.
8. Unit tests added/updated and passing.

## Out-of-Scope
- Refactoring entire conversation architecture.
- Multi-session runtime IDs.
- New UI/manager feature work unrelated to provider integration.

## Notes for Coding Agent
- Keep code changes minimal and localized.
- Prefer shared helper for AX650 reset logic to avoid duplicate endpoint code.
- Preserve current runtime behavior for non-AX650 providers.
- Add clear logs around reset actions to aid field debugging.

