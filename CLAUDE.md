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

Phase 1-3 static analysis is complete: findings P-01 to P-24. Potassium 1.6.0 is an unsigned Tauri (Rust + WebView2) application, not packed. Its cloud channels, on-disk footprint, command surface, and local MCP server (rmcp 2.2.0, JSON-RPC, bearer auth, tools `list_clients`/`execute_script`/`read_console`/clear-console) are mapped. See `docs/research/FINDINGS.md` and `docs/research/ARCHITECTURE.md`.

## What is open

Listed with priority in the README "Next steps". In short: the attach mechanism (needs disassembly of the `attach` handler), the `/resource` payload and its `/hashes` validation (needs the app running with traffic capture), and the server-crash cause (needs measurement in a researcher-owned experience). These need a desktop.

## Conventions

- Findings identifiers are `P-NN`, assigned in order, never reused.
- Evidence codes: `S` string, `I` import/export, `D:0xADDR` disassembly, `R` resource, `P:<line>` payload line, `C` controlled observation.
- Keep the research docs (`docs/research`) and the defensive docs (`docs/defense`) separate. Detection signatures belong in `detection/` and derive from recorded findings.
