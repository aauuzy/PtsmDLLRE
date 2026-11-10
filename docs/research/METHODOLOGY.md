# Methodology

How the analysis is conducted, in the order the phases run. The approach is static first: the binary is read, not executed, and the only dynamic work permitted is controlled measurement in an environment the researcher owns. Nothing is run against live Roblox games or infrastructure.

## Phase 1 — Protection and anti-analysis

Characterize what stands between the analyst and the code. Hash the sample and record it. Inspect the PE structure: sections, entropy, imports, and any overlay. Identify packing, virtualization, or a known protector. Locate integrity checks and anti-debugging. This phase gates everything after it; if the binary is virtualized, the later phases proceed against whatever can be recovered, and the limits are recorded in [`LIMITATIONS.md`](LIMITATIONS.md).

## Phase 2 — Attach mechanism

Determine how the loader introduces Potassium's code to the Roblox client, statically from the loader and injected component.

## Phase 3 — Execution model and local channels

Map how script is submitted and executed and what local interface carries it, including any localhost server, pipe, or shared-memory channel and its message format.

## Phase 4 — Resource handling

Recover embedded scripts and data, reverse any encryption or compression, and identify remote endpoints contacted for updates or payloads.

## Phase 5 — Server-impact capability (primary)

Reproduce the RemoteEvent flood only in a private experience owned by the researcher, with remotes under the researcher's control. Measure what triggers the shutdown: the call rate, the payload, and whether a server-side rate limit and argument validation prevent it. The goal is to classify the cause as game-level or engine-level. This is the project's primary objective and the one most likely to be mistaken; it is held to the confirmed-evidence bar before any conclusion is recorded.

## Phase 6 — Defense

Produce detection signatures from the static findings, and developer-side countermeasures for the server-impact class: server-authoritative rate limiting, argument validation, and flood detection.

## Verification

Every claim is tied to evidence in [`FINDINGS.md`](FINDINGS.md) before it is stated anywhere else. Disassembly citations are re-read against the binary rather than quoted from memory. Where a claim cannot be verified, it is marked tentative or left out.
