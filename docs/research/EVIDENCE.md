# Evidence

The concrete strings and structural values behind the Phase 1-3 findings, so each claim in [`FINDINGS.md`](FINDINGS.md) can be checked against what was actually read from `Potassium.exe`. Quotes are short excerpts of identifier and description strings, included for research and detection. This is the static-analysis counterpart to a disassembly appendix; disassembly excerpts will be added when the attach work is done.

## Identity and version (P-01)

Version-info string table: `ProductName = Potassium`, `FileDescription = Potassium`, `FileVersion = 1.6.0`, `ProductVersion = 1.6.0`, `CompanyName = pot`.

## Sections and entropy (P-02, P-03)

```
.text    entropy 6.25
.rdata   entropy 7.38
.data    entropy 4.02
.pdata   entropy 6.82
.rsrc    entropy 7.97
.reloc   entropy 5.48
```

A `.text` entropy of 6.25 is ordinary compiled code; a packed or virtualized code section is typically near 8. No overlay.

## Signing (P-04)

Security data directory: virtual address 0, size 0. No Authenticode signature present.

## Framework (P-05, P-16)

Marker counts in the file: `tauri` 184, `TAURI` 61, `webview` 133, `WebView2` 13, `rust` 992. Frontend asset paths: `/index.html`, `/assets/index-EIR5Y9u7.js`, `/assets/index-Ljal0590.css`, Tauri `ipc.js` and `isolation_secure.js`.

## Luau and hooks (P-06)

Present strings: `Luau` (472), `loadstring` (14), `hookfunction` (1), `hookmetamethod` (1), `RemoteEvent` (8), `FireServer` (2), `Roblox` (85).

## On-disk footprint (P-10)

Shortcut targets: `%LOCALAPPDATA%\Potassium\workspace`, `%LOCALAPPDATA%\Potassium\autoexec`, `%LOCALAPPDATA%\Potassium\scripts`.

## Remote channels (P-11, P-12)

`https://api.potassium.pro/login`, `https://chat.potassium.pro/chat`, `https://files.potassium.pro/` with route fragments `/version`, `/resource`, `/hashes`, `/gui_name`.

## Dependency SBOM (P-19)

From embedded crate paths, e.g. `index.crates.io-...\rmcp-2.2.0`, `...\tauri-2.11.2`, `...\axum-0.8.9`, `...\hyper-1.10.1`, `...\reqwest-0.12.28`, `...\rustls-0.23.41`, `...\tungstenite-0.29.0`, `...\cfb-0.7.3`, `...\brotli-decompressor-5.0.1`. Own source path `src\mcp.rs` and type `potassium_tauri_lib::mcp::TabInfo`.

## MCP server (P-17, P-18, P-23)

- Auth: `A valid Potassium MCP bearer token is required.` (near `src\mcp.rs`)
- Protocol: `MCP-Protocol-Version` with value `2025-03-26`; errors `Unsupported MCP-Protocol-Version:` and `Session ID is required`.
- Port validation: `MCP port must be between 1024 and 65535.` near `127.0.0.1`.
- AI-tool registration: references to `claude-code`, `codex`, `cursor`, `vscode`, with `.claude.json`, `config.toml`, `mcp.json`, `CLAUDE_CONFIG_DIR` and connection states `connected`/`notConnected`/`outdated`/`unreadable`.
- JSON-RPC methods: `initialize`, `tools/list`, `tools/call`, `resources/list`, `prompts/list`, `ping`, `notifications/initialized`, `notifications/progress`, `notifications/cancelled`.

## MCP tools (P-21, P-24)

- `execute_script`, input type `potassium_tauri_lib::mcp::ExecuteScriptInput`; returns a console cursor.
- `read_console`, described as `Read captured console output`; parameters `after_cursor` and `wait_ms` ("wait briefly for asynchronous script output").
- `list_clients`, output type `ListClientsOutput`, described as to be called "before choosing a PID for execute_script".
- A clear-console tool: "Clear Potassium's console: the history read_console returns and the console panel in the app."

## Local address (P-14)

`127.0.0.1:8224` (observed twice), `127.0.0.1/mcp`, and `127.0.0.1:34254`. `localhost:1420` also present (Tauri default dev-server port; treated as a build artifact).

## Absent injection primitives (P-25)

Import table (kernel32 131, ntdll 9) contains OpenProcess, QueryFullProcessImageNameW, CreateToolhelp32Snapshot, Process32FirstW, Process32NextW, GetProcessTimes, TerminateProcess, DuplicateHandle, LoadLibraryA/W/ExA/ExW, GetProcAddress, CreateProcessW, VirtualProtect (local), CreateThread (local). It contains **none** of: VirtualAllocEx, WriteProcessMemory, ReadProcessMemory, CreateRemoteThread, VirtualProtectEx, OpenThread, GetThreadContext, SetThreadContext, QueueUserAPC, NtWriteVirtualMemory, NtAllocateVirtualMemory, NtProtectVirtualMemory, NtCreateThreadEx, NtMapViewOfSection. Those names also have 0 ascii and 0 utf-16 string matches in the file, so they are not GetProcAddress-resolved. ntdll imports are only file/pipe/ioctl and version/status helpers.

## Attach handler (P-26, P-27, P-29)

`src\injector.rs`, handler func `0x3A67D0`. Helpers: `0x3A7C90` (CreateToolhelp32Snapshot + Process32FirstW/NextW + CloseHandle), `0x3A79C0` (OpenProcess + QueryFullProcessImageNameW + CloseHandle). At `0x3A6802`: `lea rdx, [rip+...]` → `"RobloxPlayerBeta.exe"`, then `call 0x3A7C90`.

Strings referenced from `0x3A67D0`: `"No Roblox client found. Start the game, then attach."`, `"Injector not found. Turn off your antivirus and restart Potassium."`, `"Injection failed (exit code N)"`.

`AttachError` builder `0x3A82E0`, concatenated field/variant run: `AttachError` `kind` `channelMismatch` `pid` `installDir` `message` `#could not close the Roblox client: `.

## Runtime-downloaded binaries (P-28)

Resource/download func `0x19B610` (files.rs). String refs: `https://files.potassium.pro/resource`, `https://files.potassium.pro/hashes`, response field run `versiondescriptioniconswebsiteUrlrootsrole`, `"resource response is missing 'version'"`, `"Couldn't reach the download server: "`. Download-name run (file offset 0x15778B9): `...dll` → `Potassium.dll`, `...exe` → `Potassium.exe`, `Decompiler.exe`, with base `https://files.potassium.pro/`. Shipped package contents (app/extracted): `Potassium.exe`, `msvcp140.dll`, `vcruntime140.dll`, `vcruntime140_1.dll`, `autoexec.lnk`, `scripts.lnk`, `workspace.lnk` — none of the three downloaded files.

## Execution channel (P-30, P-31)

`src\ws.rs`, address `127.0.0.1:8224`, message field run `actioncontenttabstabmessage`. MCP path `http://127.0.0.1:<port>/mcp` from `src\mcp.rs` (separate). Luau VM strings near func `0xE192C0`: `"%s: bytecode version mismatch (expected [%d..%d], got %d)"`, `"bytecode type version mismatch"`, `LuauCostModel`, `LuauUdataDirectAccess`.

## Command surface (P-32)

Command-name blob at file offset 0x15E3D78: `...repair_client` `pid` `installDir` `set_always_on_top` `window` `on` `attach` `autologin` `username` `password` `kill_clients` `pids` `compile_moonscript` `engine` `explore_fetch` `url` `download_binaries` `luau_complete` `line` `column`; adjacent chat run: `source` `chat_send` `messages` `set_mcp_enabled` `state` `manager` `enabled` `port`, with `https://chat.potassium.pro/chat` and `src\chat.rs`.

## Self-update (P-33)

Batch-script fragment (file offset ~0x1577C77): `... >nul` / `if errorlevel 1 goto gone` / `ping -n 2 127.0.0.1 >nul` / `goto wait` / `:gone` / `echo [%TIME...`.

## Decompiler child (P-34)

`src\decompiler.rs`, func `0x3A5DF0` references `Decompiler.exe` and imports `AssignProcessToJobObject`.

## Server-impact strings (P-35)

`FireServer` (2) both inside the Luau typedef blob: `"function FireServer(self, ...: any): ()"`. `RemoteEvent` occurs in the Instance class-name list (`"RemoteEvent", "UnreliableRemoteEvent"`) and the `EnumSecurityCapability` list. No native networking builds Roblox RemoteEvent frames; outbound sockets are reqwest/tungstenite to `*.potassium.pro` only.

## No kernel driver (P-36)

`DeviceIoControl` used by `0xB76560`; `NtDeviceIoControlFile` by `0xAE34B0`; `NtCreateFile` by `0xAE5AA0`; `NtCreateNamedPipeFile` by `0xB7B7C0` — all Rust async-runtime/std functions. No `\\.\<device>` path string and no `.sys` embedded; the only MZ/PE in the file is the main image at offset 0.
