# Findings

Claim ledger for the Potassium static analysis. This file is the source of truth for every factual claim the project makes. No claim appears in the README, the architecture notes, or the defensive documents unless it is recorded here first and carries supporting evidence.

Status: Phase 1-3 complete. Entries are added only after they are verified against the binary. The concrete strings and structural values behind these findings are collected in [`EVIDENCE.md`](EVIDENCE.md), and the process that produced them is in [`METHODOLOGY.md`](METHODOLOGY.md).

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

### Sample

| File | Size (bytes) | SHA-256 |
| --- | --- | --- |
| `Potassium.exe` | 28,410,368 | `78f75e896b4b5ad719bc3c79182c5d5ba2dff071dce91cc160dcdf1308b5f6ea` |
| `msvcp140.dll` | 557,728 | `0f885b509a685d2bbfa652fed26b5fb31d88fbdab0a978c641d1c7b8aa460aa9` |
| `vcruntime140.dll` | 124,544 | `d5e4d9a3e835fa679450145d6a7d94e36573a509317111904d9b3712c30d9066` |
| `vcruntime140_1.dll` | 49,792 | `1f2d41c4aa5db0bc33ebf7b66d72943a817d7ce6cbe880502a9403823633093f` |

### Phase 1

```
P-01  confirmed  S       Potassium.exe is a PE32+ x86-64 GUI executable with six sections
                         (.text .rdata .data .pdata .rsrc .reloc). Version resource:
                         ProductName "Potassium", FileVersion/ProductVersion 1.6.0,
                         CompanyName "pot". PE header TimeDateStamp 1793968995 (raw value;
                         header timestamps can be set arbitrarily and are not relied on).
P-02  confirmed  S       Section entropy: .text 6.25, .rdata 7.38, .data 4.02, .pdata 6.82,
                         .rsrc 7.97, .reloc 5.48. No overlay (raw section data ends at
                         end of file).
P-03  probable   S       The code is not packed or virtualized at the section level. A
                         .text entropy of 6.25 is typical of ordinary compiled code; a
                         packed or VM-protected code section is typically near 8. No
                         VMProtect or Themida marker strings were found. Pending
                         confirmation by reading the entry point in disassembly.
P-04  confirmed  S       The executable carries no Authenticode signature: the security
                         data directory is empty (offset 0, size 0). Contrast: Xeno
                         v1.3.65 is signed with a self-signed certificate.
P-05  probable   S       Built with Tauri (Rust backend, WebView2 frontend). Marker counts
                         in the file: "tauri" 184, "TAURI" 61, "webview" 133, "WebView2"
                         13, "rust" 992. "Electron" appears only twice and is not taken as
                         evidence of Electron.
P-06  confirmed  S       Luau-related strings are present: "Luau" 472, "luau" 30,
                         "loadstring" 14, "hookfunction" 1, "hookmetamethod" 1,
                         "RemoteEvent" 8, "FireServer" 2, "Roblox" 85. Presence only; what
                         code references them is not yet determined.
P-07  confirmed  I       Import table includes ws2_32.dll (21 functions), bcrypt.dll (1),
                         bcryptprimitives.dll (1), ntdll.dll (9), kernel32.dll (131),
                         user32.dll (121), and MSVCP140.dll (36).
P-08  confirmed  S       The package contains no separate injectable DLL. Besides
                         Potassium.exe it holds only three files named as Microsoft Visual
                         C++ runtimes and three shortcuts. Any injected component is
                         therefore embedded in Potassium.exe or obtained at runtime.
P-09  tentative  S       msvcp140.dll, vcruntime140.dll and vcruntime140_1.dll are stock
                         Microsoft redistributables. Based on name and PE type only; not
                         yet verified against Microsoft's signatures.
P-10  confirmed  S       The three shortcuts (workspace.lnk, autoexec.lnk, scripts.lnk)
                         target %LOCALAPPDATA%\Potassium\workspace, \autoexec and \scripts.
P-11  confirmed  S       Remote endpoint strings present: https://api.potassium.pro/login,
                         https://chat.potassium.pro/chat, and https://files.potassium.pro/
                         with route fragments /version, /resource, /hashes, /gui_name.
P-12  probable   S       files.potassium.pro is the update and resource-distribution
                         channel: a version string (/version), a resource bundle
                         (/resource), an integrity manifest (/hashes). This parallels
                         Xeno's remote version and resource channel. The fetch-and-use
                         logic has not been read from code.
P-13  probable   S       Command-name strings present include attach, execute, autoexec,
                         login, update. The plugin namespaces in the binary are all stock
                         Tauri core (window, menu, tray, path, app, webview, image, event,
                         opener, resources; P-05), so Potassium's own functions are plain
                         Tauri commands invoked by bare name. That each string is a
                         registered command bound to the named action is inferred from the
                         names, not yet confirmed from handler code.
P-14  probable   S       Local interface on 127.0.0.1 with a /mcp path. Observed address
                         strings 127.0.0.1:8224 and 127.0.0.1:34254. localhost:1420 is
                         Tauri's default dev-server port and is treated as a build artifact,
                         not a runtime channel.
P-15  probable   S       Potassium appears to run a local MCP (Model Context Protocol)
                         server. Identifier strings present: mcp_enabled, mcp_status,
                         mcp_servers, mcp_repl, and an adjacent port/state-manager/repair
                         reference. The purpose, programmatic or AI-driven control of the
                         executor, is inferred from these names and the chat.potassium.pro
                         endpoint, not confirmed from code.
P-16  confirmed  S       Frontend is a Vite/React bundle embedded by Tauri: /index.html,
                         /assets/index-EIR5Y9u7.js, /assets/index-Ljal0590.css, Tauri's
                         ipc.js and isolation_secure.js, bundled fonts (jetbrains-mono,
                         rubik, noto-color-emoji) and images (login-halloween.png,
                         sirmeme.png).
P-17  confirmed  S       The local MCP server is implemented with the rmcp 2.2.0 crate
                         (own source path src\mcp.rs; type potassium_tauri_lib::mcp::
                         TabInfo). Transport is Streamable HTTP (rmcp streamable_http_server
                         over axum/hyper/tower). Protocol version string "2025-03-26".
                         Authentication is a bearer token ("A valid Potassium MCP bearer
                         token is required"); sessions use an Mcp-Session-Id header. The
                         port is configurable and validated to 1024-65535, bound on
                         127.0.0.1. This confirms P-15.
P-18  confirmed  S       Potassium registers itself as an MCP server into external AI
                         coding tools. Strings reference claude-code (.claude.json,
                         CLAUDE_CONFIG_DIR), codex (config.toml), cursor (mcp.json) and
                         vscode, with connection states (connected, notConnected, outdated,
                         unreadable). The effect is to expose executor control to an
                         external AI agent as an MCP tool.
P-19  confirmed  S       Dependency SBOM, read from embedded crate paths (may be partial):
                         desktop stack tauri 2.11.2, tauri-runtime-wry 2.11.2, tao 0.35.3,
                         muda 0.19.2, softbuffer 0.4.8; HTTP server axum 0.8.9, hyper
                         1.10.1, tower 0.5.3; HTTPS client reqwest 0.12.28, rustls 0.23.41,
                         ring 0.17.14; MCP rmcp 2.2.0; WebSocket tungstenite 0.29.0;
                         serialization serde_json 1.0.150, schemars 1.2.1, toml_edit
                         0.22.24; cfb 0.7.3 (OLE/Compound File, used for .lnk shortcuts);
                         brotli-decompressor 5.0.1; base64, data-encoding, uuid 1.23.2.
P-20  probable   S       The .lnk shortcuts (P-10) are written by Potassium itself, as
                         implied by the cfb 0.7.3 dependency (the format .lnk files use).
P-21  confirmed  S       The MCP server exposes a small tool set for AI-driven control:
                         execute_script (runs a script; schema properties include script,
                         code, content), read_console (description string "Read captured
                         console output"), and attach. Together these are an execute-and-
                         observe loop an external agent can drive. Other tools may exist
                         but were not confirmed.
P-22  confirmed  S       An embedded Roblox API type-definition blob is present (roughly
                         8,193 lines of RBXScriptSignal/type declarations), consistent with
                         an in-app script editor providing Luau autocomplete. Benign in
                         itself; confirms the UI includes a script editor.
P-23  confirmed  S       The MCP server is a conformant JSON-RPC 2.0 server. Standard
                         methods present: initialize, tools/list, tools/call, resources/
                         list, prompts/list, ping, and notifications/{initialized,progress,
                         cancelled}.
P-24  confirmed  S       Fuller MCP tool set and control model, from embedded tool
                         descriptions and parameter type names. list_clients (output type
                         ListClientsOutput; "Call this before choosing a PID for
                         execute_script") enumerates attached Roblox clients by PID.
                         execute_script (input type ExecuteScriptInput) targets a PID and
                         returns a console cursor. read_console takes after_cursor and an
                         optional wait_ms ("wait briefly for asynchronous script output").
                         A clear-console tool clears "the history read_console returns and
                         the console panel in the app". Control model: list clients, pick a
                         PID, execute, read output by cursor. Extends P-21.
```

## Corrections log

Records any claim that was recorded and later changed or withdrawn, with the reason. Keeping corrections visible is part of the methodology; a finding that turns out wrong is edited here rather than deleted silently.

None yet.

## Open questions

- Is the entry point ordinary compiler-generated startup code? This would confirm P-03.
- Is the injected component embedded in Potassium.exe or obtained at runtime (P-08)?
- How does Potassium attach to the Roblox client process?
- How does it deliver and execute script, and over what local channel?
- The server-impact capability: is the server shutdown caused by volume against an unprotected RemoteEvent (game-level), or does it occur against a properly rate-limited and validated remote (engine-level)? This is the primary question and is unresolved.
