# tools

Analysis scripts. Each takes a locally supplied sample path and reads only; nothing is executed and nothing is fetched over the network.

- `inspect_pe.py` (requires `pefile`) — the Phase 1 PE inspector: headers, per-section entropy, imports, resource types, the Authenticode security directory, version-info, and a framework/marker fingerprint count. Produced findings P-01 to P-09. Run: `python3 -I inspect_pe.py <exe>`.
- `extract_strings.sh` — the Phase 2-3 string extractor: dumps the ASCII and UTF-16 string tables and runs the categorized grep passes (frontend assets, Tauri command surface, network endpoints, `potassium.pro` routes, the local MCP server, command names, Rust module paths, the crate SBOM, and the MCP/JSON-RPC protocol and tool surface). Produced findings P-10 to P-24. Run: `bash extract_strings.sh <exe>`.

Further tools (resource decryption, a scoring detector) are added as the remaining phases require them.
