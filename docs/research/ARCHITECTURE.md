# Architecture

How Potassium is built and how its parts fit together. Every factual statement in this document must trace to a finding in [`FINDINGS.md`](FINDINGS.md). Until the analysis produces those findings, the sections below are headings that describe what will be documented, not claims about the binary.

## Protection and anti-analysis

Potassium 1.6.0 ships as a single 28 MB executable built with Tauri: a Rust backend hosting a WebView2 user interface (P-01, P-05). It is unsigned (P-04).

Section entropy does not indicate packing or virtualization of the code (P-02, P-03). The perception that it is harder to analyze than Xeno comes from scale rather than protection: a large Rust binary with heavy inlining and an embedded web frontend. Integrity self-checks, anti-debugging, and any licensing layer are not yet examined.

The package holds no separate injectable DLL (P-08). The component that runs inside the Roblox client, `Potassium.dll`, is not embedded either; it is downloaded at runtime from `files.potassium.pro` (P-28, resolved below).

On disk, Potassium uses `%LOCALAPPDATA%\Potassium` with `workspace`, `autoexec`, and `scripts` folders (P-10).

## Attach mechanism

Recovered by disassembly to the level the shipped sample allows (P-25 to P-29). The `attach` handler lives in `src\injector.rs` (func `0x3A67D0`) and runs in two stages.

First, **locate the client**: it enumerates processes with `CreateToolhelp32Snapshot`/`Process32FirstW`/`Process32NextW`, matches the image name `RobloxPlayerBeta.exe`, and confirms each match with `OpenProcess` + `QueryFullProcessImageNameW`, collecting the matching PIDs (P-26). If none are found it returns "No Roblox client found. Start the game, then attach." This per-PID enumeration is what `list_clients` (P-24) reports.

Second, **inject**: the executable itself does no in-process injection. Its import table carries none of the usual primitives — no `VirtualAllocEx`, `WriteProcessMemory`, `CreateRemoteThread`, `NtWriteVirtualMemory`, `VirtualProtectEx`, `OpenThread`/`SetThreadContext` or `NtMapViewOfSection` — and none of those names appear as strings for a `GetProcAddress` lookup (P-25). Instead the handler runs a **separate injector component as a child process and branches on its exit code**: "Injector not found. Turn off your antivirus and restart Potassium." and "Injection failed (exit code N)" (P-27). The payload it maps is a DLL named `Potassium.dll`. Neither the injector nor `Potassium.dll` is in the shipped package; both are downloaded at runtime from `files.potassium.pro` (P-28), which is why antivirus removal of the downloaded file produces "Injector not found".

Attach is modeled with an `AttachError { kind, pid, installDir, message }` type whose `kind` includes `channelMismatch` (P-29). `Potassium.dll` is therefore built against a specific Roblox release channel and install, and attach can need to close/relaunch the client — the coupling that ties a working attach to `/version` and `download_binaries`. The downloaded injector's own memory-write technique (manual map vs. `LoadLibrary`, usermode vs. a brought-along driver) is not in this sample; there is no evidence of a kernel driver in the executable itself (P-36, no `\\.\` device path, no `.sys`, the ioctl/pipe imports belong to the Rust async runtime).

## Execution model

The application exposes its functions as plain Tauri commands invoked by name. The recovered command table (P-32) is: `attach`, `autologin` (`username`, `password`), `kill_clients` (`pids`), `compile_moonscript` (`engine`), `explore_fetch` (`url`), `download_binaries`, `luau_complete` (`line`, `column`), `repair_client`, `set_always_on_top`, `set_mcp_enabled` (`enabled`, `port`), `chat_send`, plus state/manager helpers. Scripts are compiled to **Luau bytecode in-process** — the binary embeds a Luau compiler/VM (`"bytecode version mismatch"`, `LuauCostModel`; P-31) — and a `compile_moonscript` path compiles MoonScript to Lua first. The bytecode is then delivered to the injected DLL over the local channel below. Self-update (P-33) downloads a new `Potassium.exe` and runs a generated batch script that waits for the old process to exit (a `ping -n 127.0.0.1` delay loop) before swapping it.

## Local control channels

Potassium runs a local MCP (Model Context Protocol) server on `127.0.0.1` at `/mcp`, observed at `127.0.0.1:8224` (P-14). It is implemented with the `rmcp` 2.2.0 crate over a Streamable-HTTP transport built on `axum`/`hyper`/`tower`, speaks MCP protocol version `2025-03-26`, authenticates with a bearer token, and tracks sessions with an `Mcp-Session-Id` header (P-17). The port is configurable and validated to the 1024-65535 range.

The purpose is confirmed by how it installs itself: Potassium writes its MCP server into the configuration of external AI coding tools, `claude-code` (`.claude.json`), `codex` (`config.toml`), `cursor` (`mcp.json`), and `vscode` (P-18). The effect is to expose executor control to an AI agent as an MCP tool, an integration Xeno does not have. It is a conformant JSON-RPC 2.0 MCP server (standard `initialize`, `tools/list`, `tools/call`, notifications; P-23). The tool set implements an attach-execute-observe loop over Roblox clients identified by process ID (P-24): `list_clients` enumerates the attached Roblox clients by PID, `execute_script` runs a script in a chosen PID and returns a console cursor, `read_console` reads output after a cursor (with an optional `wait_ms`), and a clear-console tool resets the console. So an external agent lists the running clients, picks one, runs a script, and polls its output by cursor, the same loop the GUI offers, exposed to automation. `localhost:1420` also appears but is Tauri's default dev-server port and is treated as a build artifact.

There are two local servers, and they are not the same thing (P-30). The MCP server (`src\mcp.rs`, `http://127.0.0.1:<port>/mcp`) is the AI-automation front door described above. The **executor transport** is a separate WebSocket server in `src\ws.rs` on `127.0.0.1:8224`, with a message schema of `action`, `content`, `tab`, `tabs`, `message`: this is the channel the injected `Potassium.dll` connects back to, receiving compiled script to run (by tab) and returning console output. The MCP tools and the GUI both drive the ws.rs channel; the injected DLL only ever talks to ws.rs. The second observed address `127.0.0.1:34254` appears only in a crate-path region and is left tentative.

## Technology stack

From the embedded crate paths (P-19): the desktop shell is Tauri 2.11.2 with the `wry` WebView2 runtime; the HTTP surface (MCP server) is `axum`/`hyper`/`tower`; outbound HTTPS to `*.potassium.pro` uses `reqwest` with `rustls`; WebSocket support is present via `tungstenite`; `toml_edit` edits the AI tools' config files; `cfb` writes the `.lnk` shortcuts; `brotli-decompressor` handles compressed assets or resources. This is a Rust application, which is why the native code carries no separate injectable DLL in the package.

## Resource handling

Potassium contacts `files.potassium.pro` as its update and resource-distribution channel, with route fragments `/version`, `/resource`, `/hashes`, and `/gui_name` (P-11, P-12). The download path (`files.rs`, func `0x19B610`, exposed as the `download_binaries` command) does GET `/resource`, which returns a JSON manifest (fields `version`, `description`, `icons`, `websiteUrl`, `roots`, `role`), then GET `/hashes` for an integrity manifest, then downloads three named files from `files.potassium.pro/`: **`Potassium.dll`** (the injected payload), **`Potassium.exe`** (self-update target), and **`Decompiler.exe`** (P-28). None of the three ship in the package. This is the single most load-bearing fact about the build: the shipped 28 MB executable is a launcher/updater/UI, and the parts that touch Roblox arrive over the network, matched by Roblox channel (P-29). Whether the downloaded payload is itself encrypted beyond TLS, and the exact `/hashes` validation, is a protocol-capture item (Phase 4 dynamic) and not determinable from the launcher alone. Authentication is handled against `api.potassium.pro/login`. The frontend assets themselves are a Vite/React bundle embedded in the executable (P-16). A bundled `Decompiler.exe` (also downloaded) is launched as a child inside a Windows Job object for script decompilation (P-34).

## Server-impact capability

The documented behavior is that Potassium can flood a RemoteEvent until the server process terminates. Static analysis narrows but does not close the question (P-35). Every `FireServer`/`RemoteEvent` string in the binary sits inside the embedded Luau API type-definition/autocomplete blob and the Instance/Enum name tables; there is **no native code in Potassium.exe that builds Roblox RemoteEvent traffic**, and the only outbound sockets go to `*.potassium.pro`. So the flood is not a native Potassium primitive — it is an ordinary Luau script (a loop calling `FireServer`) run through the normal execution path (compile to bytecode, send over the ws.rs channel to the injected DLL, which calls into the client's own Luau/remote machinery).

That the attack vehicle is a user script rather than native engine abuse is evidence toward the **game-level** side of the question in [`../defense/THREAT_ASSESSMENT.md`](../defense/THREAT_ASSESSMENT.md): the traffic is whatever the game's own RemoteEvents accept. It does not prove the engine is robust — a static absence of a native primitive cannot show that a well-rate-limited remote survives — so the boundary condition is still only resolvable by controlled measurement in a researcher-owned experience (Phase 5), and no conclusion is recorded until it is.
