# Countermeasures

Defensive measures against the threat Potassium represents, aimed at the two audiences who can act on it: game developers, who can harden their own remotes today, and the platform, which owns anything that proves engine-level.

The developer-side measures below are established practice for RemoteEvent abuse and hold regardless of what the Potassium analysis finds; they are the correct response to the game-level case and do no harm in any case. The Potassium-specific detection signatures are deferred to [`DETECTION.md`](DETECTION.md) and depend on findings that do not exist yet.

## Developer-side (RemoteEvent hardening)

- Server-authoritative rate limiting. Track per-player call counts for each RemoteEvent on the server and reject or drop calls above a sane threshold. The client is never trusted to limit itself. This is the single most effective defense against a volumetric flood.
- Argument validation. Check the type, size, and range of every argument on the server before acting on it. Reject malformed or oversized payloads early, before they reach expensive logic. This defends against the payload-shaped variant, where the cost is per-call rather than per-volume.
- Flood detection and response. Beyond a per-remote limit, detect a player driving abnormal aggregate remote traffic and respond: throttle, kick, or temporarily ignore. A player who trips the limit repeatedly is acting in bad faith.
- Cost awareness in handlers. Keep remote handlers cheap. Expensive work (large table operations, physics, replication fan-out) triggered directly by a client call turns a modest flood into a server-ending one. Defer, batch, or bound that work.

## Platform-side

- Only relevant if the analysis establishes an engine-level cause. If a properly defended remote can still crash the server, the platform-side countermeasures (bounding remote traffic per connection at the engine layer, hardening the deserialization path against malformed payloads) are Roblox's to design. They are not specified here because the premise is unproven; this section exists to mark where that guidance would go.

## Responsible disclosure

If the analysis finds an engine-level fault, it is reported to Roblox through their security program before any public detail, following the route described in [`../DISCLOSURE.md`](../DISCLOSURE.md). Developer-side hardening carries no such restriction and can be shared freely.
