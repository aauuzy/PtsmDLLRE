# Disclosure

How this project handles what it finds, and the line it holds between research and harm.

## Threat model

The question that governs disclosure is the same one that governs the whole project: whether Potassium's server-impact capability is a game-level denial of service or an engine-level fault. The two are disclosed differently.

| Cause | Owner | Handling |
| --- | --- | --- |
| Game-level: unprotected RemoteEvent, no server rate limit or validation | Game developer | Developer-side hardening is general knowledge and is shared openly in the defensive docs. No individual game is named as a target, and the flood is not demonstrated against anyone's game. |
| Engine-level: server fails despite proper remote defenses | Roblox | Reported privately to Roblox's security program first. No public detail, no proof-of-concept that eases reproduction, until Roblox has had the chance to respond. |

## What is withheld

- No working tooling for crashing servers, and no step-by-step reproduction that lowers the bar for someone to do it.
- No names of games observed to be affected.
- No private user data.
- If an engine-level fault is found, the detail that would let someone reproduce it is withheld from the public repository until disclosure has run its course.

## What is shared

- How the class of abuse works at a conceptual level, and the defenses against it.
- Static findings about the sample, detection signatures, and the methodology.

## Testing boundary

All dynamic work happens in a private experience owned by the researcher, with remotes under the researcher's control. Nothing in this project is tested against live Roblox games or infrastructure. This is both an ethical line and a legal one, and it is not crossed for the sake of a stronger finding.
