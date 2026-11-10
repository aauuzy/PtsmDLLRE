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

## How Phase 1-3 was performed

A record of the actual process, so the findings can be reproduced.

The package was extracted into an isolated directory; nothing in it was executed. The three bundled DLLs were identified by name and PE type as Microsoft Visual C++ runtimes and set aside. All files were hashed (SHA-256).

`Potassium.exe` was inspected statically with `pefile`: file and optional headers, the six sections with per-section Shannon entropy, the import table, resource types, the security data directory (to check for an Authenticode signature), and the version-info string table. Entropy was the basis for the not-packed assessment; the empty security directory for the unsigned finding.

The full string tables were then extracted, both ASCII (`strings -n 5`) and UTF-16LE (`strings -n 6 -e l`), to files, and read with categorized `grep` passes: framework markers (tauri, rust, webview), network endpoints, the Tauri IPC and command surface, embedded crate paths (for the dependency SBOM) and the project's own source paths, and the MCP protocol methods and tool descriptions. Findings were taken only from strings that recurred and made sense in context; coincidental substring matches in compressed regions were discarded.

Each finding's evidence code records which of these produced it.

## How Phase 2-4 was performed

The attach, execution and resource findings (P-25 to P-36) were recovered by static disassembly with `tools/xrefs.py`, which indexes functions from the `.pdata` exception table (folding chained unwind fragments into their root), disassembles each linearly with capstone, and records every RIP-relative operand and direct `call`/`jmp` edge. Nothing was executed.

The work proceeded import-first. The import table was checked for code-injection primitives; their absence, cross-checked against a whole-file ascii+utf-16 string scan for the same API names (to rule out `GetProcAddress` resolution), established P-25. The process-reach imports that *are* present (`OpenProcess`, `CreateToolhelp32Snapshot`, `Process32FirstW`, `QueryFullProcessImageNameW`, `AssignProcessToJobObject`, `CreateProcessW`) were mapped to their referencing functions, which clustered into Potassium's own low-address code and resolved to `src\injector.rs` and `src\decompiler.rs` by nearby module-path strings. The attach handler was then read directly: the `"RobloxPlayerBeta.exe"` match, the `"Injector not found"` / `"Injection failed (exit code N)"` branch, and the `AttachError` fields. The resource path was found by xref'ing the `files.potassium.pro` and `Potassium.dll` strings to `files.rs` (func `0x19B610`) and reading its `/resource`+`/hashes`+download sequence. The command table, the `ws.rs` WebSocket channel, the embedded Luau VM, and the self-update batch script were recovered from their string runs and referencing functions. The `FireServer`/`RemoteEvent` strings were located and shown to sit only in the Luau typedef blob (P-35). The entry-point confirmation of P-03 remains deferred; it is stated in `LIMITATIONS.md` rather than worked around.

To reproduce: `python tools/xrefs.py <exe> --import OpenProcess` (and the other imports), `--string "RobloxPlayerBeta.exe"`, `--string "Potassium.dll"`, `--func 0x3A67D0`, etc. The runtime-downloaded components (`Potassium.dll`, the injector, `Decompiler.exe`) are not in the sample and were not analysed.

## Verification

Every claim is tied to evidence in [`FINDINGS.md`](FINDINGS.md) before it is stated anywhere else. Disassembly citations are re-read against the binary rather than quoted from memory. Where a claim cannot be verified, it is marked tentative or left out.
