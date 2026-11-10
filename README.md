# PtsmDLLRE

Static reverse-engineering and defensive detection research on the Potassium Roblox executor.

## Overview

PtsmDLLRE is a companion to XenoDLLRE: a static analysis of a commercial Roblox executor aimed at understanding how it works and producing detection signatures and developer-side countermeasures. Potassium's distinguishing trait, relative to Xeno, is a reported ability to overwhelm a game server by flooding RemoteEvents until the server process terminates and all players are disconnected.

The central question this project exists to answer is whether that capability is:

- a game-level denial of service, where the target game exposes a RemoteEvent with no server-side rate limiting or argument validation, so the fault lies in the game's code; or
- an engine-level fault, where the Roblox server breaks regardless of how well the game defends its remotes.

The distinction determines whether the behavior is a developer-hardening concern or a platform vulnerability. The project does not assume the answer and does not record a conclusion until the binary and controlled measurement support one.

## Scope and ethics

- Analysis is performed on a legally obtained, licensed sample.
- No testing is performed against live Roblox games or infrastructure. Any dynamic verification is confined to a private experience owned by the researcher, using RemoteEvents under the researcher's control.
- The intent is defensive. The repository produces detection logic and hardening guidance; it contains no changes that improve the executor or help it evade anti-cheat.
- No private user data is collected or published.

## Status

Phase 1-4 static analysis complete (findings P-01 to P-36 in [`docs/research/FINDINGS.md`](docs/research/FINDINGS.md); summary in [`reports/POTASSIUM_ANALYSIS.md`](reports/POTASSIUM_ANALYSIS.md)). Potassium 1.6.0 is a single unsigned 28 MB Tauri application (Rust backend, WebView2 interface, Vite/React frontend), not packed or virtualized; its difficulty is size, not protection.

The headline result is that the shipped executable is a **launcher/updater/UI**: the components that actually touch Roblox — the injected `Potassium.dll`, the external injector, and `Decompiler.exe` — are **downloaded at runtime** from `files.potassium.pro` and are not in the package. Attach locates the `RobloxPlayerBeta.exe` process and hands injection to the downloaded injector (checking its exit code); the executable itself holds no code-injection APIs. Script runs as Luau compiled to bytecode in-process and shipped over a local WebSocket (`127.0.0.1:8224`, `src\ws.rs`) to the injected DLL. The RemoteEvent-flood capability is carried by a user Luau script, not a native primitive.

What remains is dynamic: the server-crash classification, plus on-the-wire capture of the resource payload and of the downloaded injector/DLL.

## Next steps

The static pass is complete. The remaining work, in priority order:

1. Server-impact capability (primary). Reproduce the RemoteEvent flood in a private experience you own, with remotes under your control, and measure whether server-side rate limiting and argument validation prevent it (Phase 5 in [`docs/research/METHODOLOGY.md`](docs/research/METHODOLOGY.md)). This is what classifies the server crash as game-level or engine-level. Static analysis (P-35) shows Potassium contributes no native flood primitive, which leans game-level, but does not close the question.
2. Downloaded components. Capture `Potassium.dll` and the injector from a researcher-owned run and read the injector's memory-write technique (manual map vs. `LoadLibrary`) — the one part of the attach chain the launcher does not contain.
3. Resource channel. Capture traffic to `files.potassium.pro` during an update to document the `/resource` JSON and `/hashes` validation on the wire (the client side is mapped in P-28).
4. Detection. Turn the static signals into the detector and YARA rules in [`docs/defense/DETECTION.md`](docs/defense/DETECTION.md); the Phase 2-4 findings give concrete host and binary indicators.

## Repository layout (planned)

```
PtsmDLLRE/
  README.md
  docs/
    research/
      FINDINGS.md        claim ledger (P-01, P-02, ...) with confidence and evidence codes
      ARCHITECTURE.md     components, attach, execution, protocol, protection
      METHODOLOGY.md      phases, tools, verification approach
      LIMITATIONS.md      what was not determined and why
    defense/
      THREAT_ASSESSMENT.md  harm model, game-level vs engine-level question
      COUNTERMEASURES.md    developer and platform hardening
      DETECTION.md          detection strategy and signatures
    DISCLOSURE.md         threat model, what is withheld, responsible-disclosure route
  detection/
    ptsm_detector.py      PE-gated scoring detector
    ptsm_executor.yar     YARA rules
  tools/                  analysis and reporting scripts
  reports/                generated sample reports
  tests/                  tool tests
```

## Findings

The findings ledger (`docs/research/FINDINGS.md`) is the source of truth. Each claim carries an identifier (P-01, P-02, ...), a confidence level, and an evidence code tying it to a disassembly line, a static string, a decrypted resource, or a controlled observation. The ledger is currently empty pending analysis.

## Research phases

1. Protection and anti-analysis: packing, obfuscation, integrity checks, anti-debugging. Reported to be stronger than Xeno, so this is the gating step.
2. Attach and injection mechanism.
3. Execution model and local control channels.
4. Resource handling: encryption, embedded scripts, remote channels.
5. Server-impact capability: reproduce in an owned experience, measure what triggers the shutdown, and determine game-level versus engine-level cause. Primary objective.
6. Defense: detection signatures, and developer-side countermeasures (remote rate limiting, argument validation, flood detection).

## Authorship

Research direction, sample acquisition and verification by Gavin Hatcher ([aauuzy](https://github.com/aauuzy)). AI assistants are used during analysis, tooling and writing; all claims are verified against the binary before being recorded.

## License

Original code and documentation: MIT ([`LICENSE`](LICENSE)). Potassium and Roblox are the property of their respective owners. Short excerpts and identifiers from Potassium's code are quoted for research and detection purposes only.
