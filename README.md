# Victoria Relay

A Home Assistant conversation agent that does exactly one thing:
relay every sentence to Victoria and return her reply.

Home Assistant's built-in conversation agent parses sentences,
matches intents, and can act on exposed devices. This integration
replaces it — for the pipelines you point at it — with a pure relay:

1. The pipeline hands the recognized sentence to this agent.
2. The agent POSTs it to a relay endpoint on the local network
   (configured in the integration's setup: URL + wait timeout).
3. The endpoint passes the sentence to Victoria and waits for her
   reply; her reply becomes the pipeline response, verbatim.

No intent matching. No device access. The agent holds no credentials
and has no control path — every decision stays with Victoria.

Design notes, cutover plan, and security notes live in
[DESIGN.md](DESIGN.md).

## Install (HACS)

Add this repository to HACS as a custom repository (category:
Integration), install "Victoria Relay", restart Home Assistant, then
add the integration and set the relay endpoint URL. Point any Assist
pipeline's conversation agent at "Victoria Relay".
