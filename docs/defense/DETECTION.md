# Detection

Strategy for detecting the Potassium sample itself, as a companion to the developer-side hardening in [`COUNTERMEASURES.md`](COUNTERMEASURES.md). Hardening stops the abuse; detection identifies the tool.

Status: pending. Detection signatures derive from static findings, and the analysis has not produced any. This document records the intended approach so the detector and rules can be built against it once Phase 1 and the resource work yield durable signals.

## Approach

The detector follows the same shape as XenoDLLRE's: a PE-gated, score-based classifier rather than a single brittle signature. A file is first confirmed to be a Windows PE of the expected architecture; only then are weighted signals summed, and a verdict is assigned by threshold. This keeps false positives down and degrades gracefully across versions, since no single signal is load-bearing.

## Candidate signal classes

To be confirmed against the binary before use:

- Code-signing identity, if the sample is signed, including the signer and whether the signature validates.
- Stable import or export contracts that the loader or injected component must expose.
- Recoverable embedded strings or resources unique to Potassium.
- Structural traits of the protection layer, if the protector leaves a consistent fingerprint.

Each signal becomes a detector weight and, where it is a byte or string pattern, a YARA rule. None is written until it is recorded as a finding with evidence. A version-independent rule, built on traits that survive updates, is preferred over one tied to a single build.

## Signals identified so far

From Phase 1-3 static analysis, concrete signals now available for the detector and for host-based detection. Each traces to a finding.

- Unsigned PE with the Tauri/Rust fingerprint: no Authenticode signature (P-04), stock Tauri core plugin namespaces, and `rmcp`/`tauri`/`wry` crate paths (P-05, P-19). File-level.
- On-disk footprint: `%LOCALAPPDATA%\Potassium\` with `workspace`, `autoexec`, `scripts`, and the three `.lnk` shortcuts (P-10). Host-based.
- Network indicators: connections to `api.potassium.pro`, `files.potassium.pro`, and `chat.potassium.pro` (P-11). Network-based.
- Local MCP server: a bearer-authenticated MCP endpoint on `127.0.0.1` at `/mcp` speaking protocol version `2025-03-26` (P-17). Host or local-network based.
- MCP config implantation: Potassium entries written into `.claude.json`, `config.toml`, `mcp.json`, or VSCode settings naming a Potassium MCP server (P-18). This is a strong, specific host-based signal, and one defenders of AI developer tools can check directly.

These are recorded here as the basis for the detector; the detector and YARA rules are written against them once the exact byte and string anchors are pinned.

## Files (pending)

- `detection/ptsm_detector.py` — the PE-gated scoring detector.
- `detection/ptsm_executor.yar` — YARA rules for the confirmed static signals.

These are created once there are findings to base them on. Writing them earlier would mean inventing signatures, which this project does not do.
