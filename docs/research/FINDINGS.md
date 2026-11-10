# Findings

Claim ledger for the Potassium static analysis. This file is the source of truth for every factual claim the project makes. No claim appears in the README, the architecture notes, or the defensive documents unless it is recorded here first and carries supporting evidence.

Status: Phase 1-4 complete; Phase 5 (server-impact) is the only remaining item and needs controlled dynamic measurement. Entries are added only after they are verified against the binary. The concrete strings and structural values behind these findings are collected in [`EVIDENCE.md`](EVIDENCE.md), and the process that produced them is in [`METHODOLOGY.md`](METHODOLOGY.md).

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

### Phase 2-4 (attach, execution, resource handling)

Recovered by static disassembly with `tools/xrefs.py` (functions from `.pdata`, RIP-relative and direct-call edges) plus targeted string context. Disassembly citations are RVAs; the image base is the PE default and addresses are re-read against the binary.

```
P-25  confirmed  I,D     Potassium.exe contains no code-injection primitives. The import
                         table has none of VirtualAllocEx, WriteProcessMemory,
                         CreateRemoteThread, NtWriteVirtualMemory, NtAllocateVirtualMemory,
                         NtCreateThreadEx, VirtualProtectEx, OpenThread, SetThreadContext,
                         QueueUserAPC or NtMapViewOfSection, and none of those names appear
                         as strings for a GetProcAddress lookup (ascii and utf-16 counts all
                         0). The only process-reach imports are OpenProcess,
                         QueryFullProcessImageNameW, CreateToolhelp32Snapshot,
                         Process32FirstW/NextW, GetProcessTimes, TerminateProcess and
                         DuplicateHandle. The executable itself therefore does not write to
                         or create a thread in the Roblox process.
P-26  confirmed  S,D     Attach handler is in src\injector.rs (func D:0x3A67D0). It locates
                         the Roblox client by enumerating processes
                         (CreateToolhelp32Snapshot/Process32FirstW/NextW in helper
                         D:0x3A7C90) and matching the image name "RobloxPlayerBeta.exe"
                         (lea at D:0x3A6802), confirming the match with
                         OpenProcess+QueryFullProcessImageNameW (helper D:0x3A79C0). Failure
                         string: "No Roblox client found. Start the game, then attach."
P-27  confirmed  S,D     Injection is delegated to a separate injector component, not done
                         in-process. The attach handler (D:0x3A67D0) runs the injector and
                         branches on its result: strings "Injector not found. Turn off your
                         antivirus and restart Potassium." and "Injection failed (exit code
                         N)" — i.e. a child process whose exit code is read. The injected
                         payload is a DLL named Potassium.dll (string present). This is why
                         P-25 holds: the memory-write work lives in the downloaded injector/
                         DLL, not in Potassium.exe.
P-28  confirmed  S,D     Potassium.dll, Potassium.exe and Decompiler.exe are obtained at
                         runtime from files.potassium.pro, not shipped. The download path
                         (files.rs, func D:0x19B610, reachable as the download_binaries
                         command) does GET /resource returning JSON (fields version,
                         description, icons, websiteUrl, roots, role; error "resource
                         response is missing 'version'"), GET /hashes (integrity manifest),
                         then downloads the three named files from files.potassium.pro/. The
                         shipped package holds none of them (only Potassium.exe, three MSVC
                         runtimes, four .lnk). Resolves P-08: the injected component is
                         obtained at runtime.
P-29  confirmed  S,D     Attach failures are modeled as AttachError (builder D:0x3A82E0) with
                         fields kind, pid, installDir, message; kind values include
                         channelMismatch, and one message is "could not close the Roblox
                         client". The installDir and channelMismatch fields show the injected
                         DLL is matched to a specific Roblox release channel/install, and
                         that attach may need to close/relaunch the client. This explains the
                         coupling between /version, download_binaries and a working attach.
P-30  confirmed  S       The local execution channel is a WebSocket server on 127.0.0.1:8224
                         implemented in src\ws.rs, with message schema fields action,
                         content, tab, tabs, message. This is the control channel between the
                         Potassium backend and the injected Potassium.dll (script in, console
                         out). It is distinct from the MCP server (src\mcp.rs, http://
                         127.0.0.1:<port>/mcp; P-14, P-17): ws.rs is the executor transport,
                         mcp.rs is the AI-automation front door that drives it. The second
                         address 127.0.0.1:34254 (P-14) appears only in a crate-path region
                         and is left tentative, not treated as a Potassium runtime channel.
P-31  confirmed  S       An embedded Luau compiler/VM is present: strings "bytecode version
                         mismatch (expected [%d..%d], got %d)", "bytecode type version
                         mismatch", LuauCostModel, LuauUdataDirectAccess (near func
                         D:0xE192C0). Scripts are compiled to Luau bytecode in-process before
                         being handed to the execution channel. A compile_moonscript command
                         (MoonScript source, P-32) and a luau_complete autocomplete command
                         also exist.
P-32  confirmed  S       Full Tauri command-name table (at 0x15E3D78): attach, autologin,
                         username, password, kill_clients, pids, compile_moonscript, engine,
                         explore_fetch, url, download_binaries, luau_complete (line, column),
                         repair_client, installDir, set_always_on_top, window, on, source,
                         chat_send, messages, set_mcp_enabled, state, manager, enabled, port.
                         Extends P-13 from five inferred names to the recovered set.
P-33  confirmed  S       Self-update uses a generated batch script with a ping-delay wait
                         loop ("ping -n 2 127.0.0.1 >nul", "goto wait", ":gone"): it waits
                         for Potassium.exe to exit, then swaps in the newly downloaded
                         Potassium.exe (fetched via download_binaries, P-28). Standard
                         self-replacing-updater pattern.
P-34  confirmed  S,D     Potassium runs a separate Decompiler.exe child inside a Windows Job
                         object (AssignProcessToJobObject, func D:0x3A5DF0, src\decompiler.rs)
                         for script decompilation. Decompiler.exe is downloaded via the
                         resource channel (P-28), not shipped.
P-35  probable   S       The server-impact capability is script-driven, not a native
                         primitive in Potassium.exe. Every FireServer/RemoteEvent occurrence
                         sits inside the embedded Luau API type-definition / autocomplete
                         blob ("function FireServer(self, ...: any): ()"; the Instance
                         class-name list "RemoteEvent","UnreliableRemoteEvent"; the
                         EnumSecurityCapability list), and the binary contains no native code
                         that constructs Roblox RemoteEvent traffic. The flood is therefore
                         produced by a user Luau script run through the normal execution path
                         (P-30, P-31), consistent with a game-level DoS against an unthrottled
                         / unvalidated RemoteEvent rather than an engine-level Potassium
                         exploit. This does not prove the engine is robust; it shows Potassium
                         adds no native flood primitive. Final game-vs-engine classification
                         still needs Phase 5 measurement.
P-36  probable   I,D     No evidence of a kernel-mode driver. The DeviceIoControl,
                         NtDeviceIoControlFile, NtCreateFile and NtCreateNamedPipeFile imports
                         are used only by Rust async-runtime functions (D:0xB76560,
                         D:0xAE34B0, D:0xAE5AA0, D:0xB7B7C0 — mio/tokio AFD socket polling and
                         std named-pipe/process plumbing), and no \\.\ device path or .sys
                         resource is present. Attach does not go through a loaded cheat
                         driver at this level.
```

## Corrections log

Records any claim that was recorded and later changed or withdrawn, with the reason. Keeping corrections visible is part of the methodology; a finding that turns out wrong is edited here rather than deleted silently.

None yet.

## Open questions

- Is the entry point ordinary compiler-generated startup code? This would confirm P-03. (Not re-examined; low priority — P-25/P-26/P-36 already read substantial native code and found ordinary compiled Rust.)
- ~~Is the injected component embedded in Potassium.exe or obtained at runtime (P-08)?~~ Resolved: obtained at runtime (P-28).
- ~~How does Potassium attach to the Roblox client process?~~ Resolved to the level the sample allows: locate RobloxPlayerBeta.exe, then a downloaded external injector maps Potassium.dll (P-26, P-27, P-28, P-29). The injector's own memory-write technique is not in this sample because the injector is downloaded, not shipped.
- ~~How does it deliver and execute script, and over what local channel?~~ Resolved: Luau compiled to bytecode in-process (P-31) and carried over a WebSocket channel on 127.0.0.1:8224 (src\ws.rs, P-30) to the injected DLL.
- The server-impact capability: is the server shutdown caused by volume against an unprotected RemoteEvent (game-level), or does it occur against a properly rate-limited and validated remote (engine-level)? Still the primary open question. P-35 narrows it — Potassium contributes no native flood primitive, so the flood is an ordinary Luau script — but the final classification needs Phase 5 controlled measurement.
- What memory-write technique does the downloaded injector use, and is Potassium.dll a manual-mapped module or a LoadLibrary target? Not answerable from this sample; needs the downloaded injector/DLL captured from a researcher-owned run.
