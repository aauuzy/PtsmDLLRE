# Threat Assessment

What harm Potassium can do, who bears it, and the single question that determines whether its most notable capability is a game bug or a platform bug. This document reasons about the threat; it does not assert facts about the binary, which live in [`../research/FINDINGS.md`](../research/FINDINGS.md).

## The central question

Potassium is reported to crash a game server by flooding a RemoteEvent until the server terminates and every player is disconnected. The capability only matters once its cause is known, and there are two very different causes:

- Game-level. The target game exposes a RemoteEvent that the server handles without a rate limit and without validating the argument. A client that calls it fast enough, or with a large enough payload, overwhelms the server script. The fault is in the game's code. Roblox gives developers the tools to prevent this, and the fix is the developer's to apply.
- Engine-level. The server process fails regardless of how carefully the game defends its remotes: a properly rate-limited, validated remote still brings the server down, or a small number of malformed packets does. Here the fault is in the platform's handling of remote traffic, and the fix is Roblox's.

These are not two severities of the same finding; they are two different findings with different owners. A report that treats a game-level flood as a platform vulnerability will be closed as out of scope, and should be. The project does not assume the answer. It is resolved only by reproducing the behavior in a researcher-owned experience and testing whether server-side rate limiting and argument validation stop it.

## Harm model

Independent of which cause holds, the observed effect is a denial of service against everyone in the affected server instance: all players are disconnected, and play in that instance stops until a new instance starts. Unlike a client-side cheat whose effect is mostly confined to the person running it, this affects other players and the game's developer, who did nothing to invite it. That is what makes the capability worth understanding carefully.

## Prevalence

Not estimated. The project makes no claim about how many people use Potassium or how often this capability is used. Any such number would be a guess, and guesses are not recorded here.

## What is not claimed

- That Potassium exploits a Roblox platform vulnerability. That is the open question, not a premise.
- That the capability works against a well-defended game. Unknown until measured.
- That this behavior is novel. Volumetric abuse of unprotected remotes is a known class; whether Potassium does anything beyond it is what the analysis is for.
