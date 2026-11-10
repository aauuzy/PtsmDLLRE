# Limitations

What this analysis does not establish, and why. Recording limits honestly is part of the method; it keeps the findings from being read as broader than the evidence supports.

## Current limitations

- The attach, execution and resource phases are resolved only to the boundary of the shipped sample. The sample is a launcher/updater/UI; the parts that touch Roblox (`Potassium.dll`, the injector, `Decompiler.exe`) are downloaded at runtime (P-28) and are therefore not in the binary that was analysed. The downloaded injector's memory-write technique, and whether `Potassium.dll` is manual-mapped or `LoadLibrary`-loaded, are not determined and need those files captured from a researcher-owned run.
- The `/resource` and `/hashes` exchange is read from the client's request-building code (P-28), not from a captured response. Whether the downloaded payload is encrypted beyond TLS, and the exact `/hashes` verification, are protocol-capture items.
- The disassembly findings (P-25 to P-36) rest on `.pdata`-derived functions and direct/RIP-relative edges (see `tools/xrefs.py` limits): leaf functions without unwind data and pointers passed through registers or vtables are not indexed. "Not referenced" means not directly referenced, not proven unused. The absent-import conclusion (P-25) is stronger, as it rests on the import table and whole-file string scan, not on the xref graph.
- The "not packed" conclusion (P-03) rests on entropy and absent marker strings; it is corroborated but not formally confirmed by an entry-point trace. P-25/P-26/P-36 read substantial ordinary compiled Rust, consistent with not-packed.
- The framework identification (P-05) rests on string counts, now corroborated by named own-source modules (`src\injector.rs`, `src\mcp.rs`, `src\ws.rs`, `src\files.rs`, `src\decompiler.rs`, `src\chat.rs`).
- The server-impact capability has not been reproduced or measured. P-35 shows Potassium adds no native flood primitive (the flood is a Luau script), which leans game-level, but the game-level versus engine-level question is not closed and neither answer is assumed.

## Standing limitations

- The analysis covers one version of one sample. Behavior may differ across versions.
- No testing is performed against live Roblox games or infrastructure, so any claim about server behavior rests on controlled measurement in a researcher-owned experience, which may not match production exactly.
- The project does not attempt to identify Potassium's authors or operators, and does not collect or publish user data.
