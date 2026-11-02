# Victoria Relay — a Home Assistant conversation agent that relays to Victoria

Commissioned by David, 2026-11-02 00:54 CST: "I'm having you get on the
task of setting up a custom agent that simply relays to you."

## Why

On the Show's voice path, HA's built-in conversation agent
(conversation.home_assistant) still parses every sentence: it matches
intents against exposed entities and authors every pipeline response.
As of 2026-11-02 00:55 CST the actuation surface is closed (all 106
Assist-exposed entities unexposed "for security"; reversal list saved
in hidden_files/assist-exposed-backup-20261102.json) and its speech is
voided by the victoria-mute black-hole TTS. The relay agent removes
the built-in agent from this pipeline entirely: sentences go to
Victoria, responses come from Victoria. No intent matching, no
nonsense — in the logs or anywhere else.

## Shape

1. **HA custom integration `victoria_relay`** (this folder; installed
   via HACS as a custom repository). Registers a conversation agent.
   On each pipeline run, `async_process`:
   - POSTs `{id, text, language}` to the relay endpoint
     (default `http://192.168.51.132:10204/utterance`, configurable in
     the config flow, along with the wait timeout, default 50 s).
   - The endpoint returns `{speech}` — Victoria's actual reply text —
     which becomes the pipeline response verbatim.
   - On timeout: returns the holding line "One moment." (inaudible
     while the pipeline TTS is victoria-mute; Victoria still delivers
     the real answer through the Show speaker when it's ready).
   - On connection error: returns a short error line (likewise
     inaudible under the mute) and logs the failure in HA.

2. **Relay endpoint on hastur** (NOT in the repo; separate small
   service, to be built with the integration): an HTTP server on
   :10204 that
   - appends the utterance to `~/voice-events.log` in the exact JSONL
     format the push listeners already consume
     (`{"kind": "heard", "text": ..., "via": "relay", "id": ...}`), so
     the existing wake chain picks it up unchanged;
   - waits for `~/relay-replies/<id>.txt` to appear (Victoria writes
     it as part of answering), up to the timeout;
   - returns its contents as `{speech}`.

3. **Victoria's side** (standing behavior, extends the current
   handoff rule): on a relay wake — spawn the next listener, do the
   work, write the reply text to the relay spool AND speak it through
   the Show via speak_show.py (the audible path, unchanged). The
   pipeline response and the spoken words are the same text, authored
   once.

## Cutover plan

- Build endpoint + integration; syntax-check both off-device.
- David adds the repo to HACS (custom repository URL) and installs —
  the one step that needs his hands (repo hosting: a GitHub repo under
  his control; credentials via the Secure Vault when we get there).
- Restart HA; add the "Victoria Relay" integration; point the
  **Victoria pipeline's** conversation_engine at it. The built-in
  "Home Assistant" pipeline stays exactly as it is for app use.
- Then drop `sensor.victoria_last_heard` from the hastur watcher's
  WATCH map (the relay line becomes the single heard-feed; last_reply
  stays watched for audit). Until cutover, dedupe identical heard
  texts within ~15 s.
- Test battery: time question, camera request, a device command, a
  nonsense sentence, a long task (ack rule: the holding line +
  Victoria's spoken ack cover the wait).

## Later (v2, only if David wants it)

Restore `tts.victoria` (the real voice shim) on the Victoria pipeline
so the pipeline itself speaks Victoria's relayed words — the relay
makes that safe, since the only text it would ever speak is hers.
v1 keeps victoria-mute: zero risk of a stray HA-authored syllable.

## Security notes

- The relay endpoint binds on hastur's LAN address only; utterances
  never leave the house network on this leg.
- The agent holds no credentials; it can only POST text and read a
  reply. Compromise of the integration yields a sentence-forwarder,
  not a control path — all actuation decisions stay with Victoria.
