# CLAUDE.md

Context for any Claude session working in this repository.

## What this is

PtsmDLLRE is static reverse-engineering and defensive research on the Potassium Roblox executor, a companion to XenoDLLRE. The goal is to understand how Potassium works and to produce detection signatures and developer-side countermeasures. It is a portfolio and anti-cheat research project, not an executor project.

## Scope rules (do not cross)

- Static analysis only. Do not test against live Roblox games or infrastructure. Any dynamic work happens only in a private experience the researcher owns, with remotes under the researcher's control.
- Defensive intent only. Do not add code whose purpose is to improve unauthorized execution or bypass anti-cheat. Document and detect the attach and execution techniques; do not reproduce a working version of them.
- No private user data. Do not name specific games as attack targets.
- Evidence discipline. Every factual claim traces to an entry in `docs/research/FINDINGS.md` with a confidence level and an evidence code. Nothing is asserted without evidence; mark `tentative`/`probable`/`confirmed` honestly, and never present an assumption as a fact.

## Current state

Phase 1-4 static analysis is complete: findings P-01 to P-36. Potassium 1.6.0 is an unsigned Tauri (Rust + WebView2) launcher, not packed. Mapped: cloud channels, on-disk footprint, full command surface, the local MCP server, and — new in Phase 2-4 — the attach mechanism, the runtime-download model, the local executor channel, and the server-impact vehicle. Key result: the shipped 28 MB exe is a launcher/updater/UI; the parts that touch Roblox (`Potassium.dll`, the injector, `Decompiler.exe`) are **downloaded at runtime** from `files.potassium.pro` and are not in the sample. Attach locates `RobloxPlayerBeta.exe` and delegates injection to a downloaded child injector (exit-code checked); the executable has **no in-process injection primitives** (P-25). Execution: Luau compiled to bytecode in-process, carried over a WebSocket on `127.0.0.1:8224` (`src\ws.rs`) to the injected DLL. The RemoteEvent flood is a user Luau script, not a native primitive (P-35). See `docs/research/FINDINGS.md`, `ARCHITECTURE.md`, and `reports/POTASSIUM_ANALYSIS.md`.

## What is open

One item remains, and it is dynamic: the server-impact classification (Phase 5) — reproduce the flood in a researcher-owned experience and measure whether server-side rate limiting and argument validation stop it (game-level vs engine-level). Two secondary items also need a running app and are not blockers for the report: capturing the `/resource` payload and `/hashes` validation on the wire, and capturing the downloaded injector/`Potassium.dll` to read its memory-write technique. All are stated in `LIMITATIONS.md` rather than worked around.

## Conventions

- Findings identifiers are `P-NN`, assigned in order, never reused.
- Evidence codes: `S` string, `I` import/export, `D:0xADDR` disassembly, `R` resource, `P:<line>` payload line, `C` controlled observation.
- Keep the research docs (`docs/research`) and the defensive docs (`docs/defense`) separate. Detection signatures belong in `detection/` and derive from recorded findings.
