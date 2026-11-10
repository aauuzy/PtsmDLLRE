# Findings

Claim ledger for the Potassium static analysis. This file is the source of truth for every factual claim the project makes. No claim appears in the README, the architecture notes, or the defensive documents unless it is recorded here first and carries supporting evidence.

Status: empty. Static analysis has not begun. Entries are added only after they are verified against the binary.

## Format

Each finding is recorded as:

```
P-NN  [confidence]  [evidence]  Statement
```

- Identifier: `P-01`, `P-02`, ... assigned in order, never reused.
- Confidence: `confirmed` (directly observed and reproduced), `probable` (strong indirect evidence), `tentative` (single weak signal, needs corroboration).
- Evidence code:
  - `S` static string in the binary
  - `I` import or export table entry
  - `D` disassembly, cited as `D:0xADDR`
  - `R` decrypted or extracted resource
  - `P:<line>` a specific line in an extracted script or payload
  - `C` controlled observation in a researcher-owned environment

A finding may carry more than one evidence code. A statement with no evidence code does not belong in this file.

## Findings

None yet.

## Corrections log

Records any claim that was recorded and later changed or withdrawn, with the reason. Keeping corrections visible is part of the methodology; a finding that turns out wrong is edited here rather than deleted silently.

None yet.

## Open questions

- Does the sample use packing, virtualization, or other anti-analysis protection, and of what kind? (Phase 1, gating.)
- How does Potassium attach to the Roblox client process?
- How does it deliver and execute script, and over what local channel?
- The server-impact capability: is the server shutdown caused by volume against an unprotected RemoteEvent (game-level), or does it occur against a properly rate-limited and validated remote (engine-level)? This is the primary question and is unresolved.
