# Potassium 1.6.0 — Static Reverse-Engineering Report

Static analysis of the Potassium Roblox executor, Phases 1–4. This report consolidates the findings ledger ([`../docs/research/FINDINGS.md`](../docs/research/FINDINGS.md), P-01…P-36) into a submission-ready summary. Every claim here traces to a numbered finding; the concrete strings and addresses are in [`../docs/research/EVIDENCE.md`](../docs/research/EVIDENCE.md). No executor, payload, or exploit code is reproduced.

## Sample

| File | Size (bytes) | SHA-256 |
| --- | --- | --- |
| `Potassium.exe` | 28,410,368 | `78f75e896b4b5ad719bc3c79182c5d5ba2dff071dce91cc160dcdf1308b5f6ea` |

Unsigned PE32+ x86-64 GUI executable, six sections, no overlay, not packed or virtualized (P-01…P-04). Built with Tauri 2.11.2 (Rust backend, WebView2 UI, Vite/React frontend) (P-05, P-16, P-19).

## Headline result

**The shipped 28 MB executable is a launcher, updater, and UI. The components that actually touch Roblox are downloaded at runtime and are not in the package.**

The shipped package contains only `Potassium.exe`, three Microsoft Visual C++ runtime DLLs, and four `.lnk` shortcuts (P-08). The parts that make Potassium an executor — the injected `Potassium.dll`, the external injector, and `Decompiler.exe` — are fetched over the network from `files.potassium.pro` on demand (P-28). This single fact explains the rest of the architecture and reshapes how the tool should be detected and disclosed.

## Attach mechanism (Phase 2)

Resolved to the boundary of the shipped sample (P-25…P-29, P-36). The `attach` handler is in `src\injector.rs` (function `0x3A67D0`) and runs in two stages.

1. **Locate the client.** It enumerates processes with `CreateToolhelp32Snapshot` / `Process32FirstW` / `Process32NextW`, matches the image name `RobloxPlayerBeta.exe`, and confirms each with `OpenProcess` + `QueryFullProcessImageNameW`, collecting the matching PIDs (P-26). No match → `"No Roblox client found. Start the game, then attach."` This enumeration is what the `list_clients` MCP tool reports.

2. **Inject — delegated, not in-process.** `Potassium.exe` imports **none** of the usual injection primitives (`VirtualAllocEx`, `WriteProcessMemory`, `CreateRemoteThread`, `NtWriteVirtualMemory`, `VirtualProtectEx`, `OpenThread`/`SetThreadContext`, `NtMapViewOfSection`), and none of those names appear as strings for a `GetProcAddress` lookup (P-25). Instead the handler runs a **separate injector as a child process and branches on its exit code** — `"Injector not found. Turn off your antivirus and restart Potassium."` and `"Injection failed (exit code N)"` (P-27). The payload mapped into the client is a DLL named `Potassium.dll`.

Attach is modeled as `AttachError { kind, pid, installDir, message }` with `kind` including `channelMismatch` (P-29): `Potassium.dll` is built against a specific Roblox release channel/install, which is why a working attach is coupled to `/version` and `download_binaries`. There is no evidence of a kernel-mode driver in the executable — no `\\.\` device path, no `.sys`, and the `DeviceIoControl`/`Nt*File` imports belong to the Rust async runtime (P-36). The downloaded injector's own memory-write technique is not in this sample and is the one remaining gap in the attach chain.

## Execution model (Phase 3)

Functions are plain Tauri commands invoked by name. Recovered command surface (P-32): `attach`, `autologin` (`username`, `password`), `kill_clients` (`pids`), `compile_moonscript` (`engine`), `explore_fetch` (`url`), `download_binaries`, `luau_complete` (`line`, `column`), `repair_client`, `set_always_on_top`, `set_mcp_enabled` (`enabled`, `port`), `chat_send`, plus state/manager helpers.

Scripts are compiled to **Luau bytecode in-process** — the binary embeds a Luau compiler/VM (`"bytecode version mismatch"`, `LuauCostModel`; P-31) — and `compile_moonscript` compiles MoonScript to Lua first. The bytecode is delivered to the injected DLL over a **local WebSocket server on `127.0.0.1:8224`** (`src\ws.rs`, message schema `action` / `content` / `tab` / `tabs` / `message`; P-30). The injected `Potassium.dll` connects back to this channel, receives script to run per tab, and returns console output.

Two local servers exist and are distinct: `src\ws.rs` (`127.0.0.1:8224`) is the executor transport; `src\mcp.rs` (`http://127.0.0.1:<port>/mcp`) is the AI-automation front door (bearer-authenticated MCP, P-14/P-17/P-24) that drives the same channel. Self-update downloads a new `Potassium.exe` and runs a generated batch script that waits for the old process to exit (a `ping -n 127.0.0.1` delay loop) before swapping it (P-33).

## Resource and update channel (Phase 4)

`files.rs` (function `0x19B610`, the `download_binaries` command) performs (P-28):

- `GET https://files.potassium.pro/resource` → JSON manifest (`version`, `description`, `icons`, `websiteUrl`, `roots`, `role`).
- `GET https://files.potassium.pro/hashes` → integrity manifest.
- Downloads `Potassium.dll`, `Potassium.exe`, and `Decompiler.exe` from `files.potassium.pro/`.

Authentication is against `api.potassium.pro/login`; chat is `chat.potassium.pro/chat`. `Decompiler.exe` (also downloaded) runs as a child process inside a Windows Job object for script decompilation (`src\decompiler.rs`, P-34). Whether the downloaded payload is encrypted beyond TLS, and the exact `/hashes` verification, are on-the-wire items; the client-side request building is mapped but the responses were not captured.

## Server-impact capability (Phase 5 — the primary question)

Static analysis narrows but does not close the game-level vs. engine-level question (P-35). Every `FireServer` / `RemoteEvent` string in the binary sits inside the embedded Luau API type-definition / autocomplete blob and the Instance / Enum name tables; **there is no native code in `Potassium.exe` that builds Roblox RemoteEvent traffic**, and the only outbound sockets go to `*.potassium.pro`. The flood is therefore an ordinary **Luau script** (e.g. a loop calling `FireServer`) run through the normal execution path, not a native Potassium primitive.

This is evidence toward the **game-level** side — the traffic is whatever the game's own RemoteEvents accept — but it does **not** prove the engine is robust. A static absence of a native primitive cannot show that a well-rate-limited, validated remote survives the volume. The boundary condition is resolvable only by controlled measurement in a researcher-owned experience (Phase 5), and no conclusion is recorded until it is. See [`../docs/defense/THREAT_ASSESSMENT.md`](../docs/defense/THREAT_ASSESSMENT.md).

## What this means for detection and disclosure

- Watching the Potassium process for the classic `VirtualAllocEx`/`WriteProcessMemory`/`CreateRemoteThread` sequence will miss the injection; it is performed by a downloaded child injector (P-25, P-27). Watch the child process and handle-opens of `RobloxPlayerBeta.exe` instead.
- Strong host indicators: `Potassium.dll` on disk or mapped into `RobloxPlayerBeta.exe`; a WebSocket listener on `127.0.0.1:8224`; `%LOCALAPPDATA%\Potassium\` with `workspace`/`autoexec`/`scripts`; a Potassium MCP entry implanted in `.claude.json` / `config.toml` / `mcp.json` / VSCode settings (P-18).
- Durable YARA anchors (launcher): `"No Roblox client found. Start the game, then attach."`, `"Injector not found. Turn off your antivirus and restart Potassium."`, `"Injection failed (exit code"`, and the module paths `src\injector.rs` / `src\ws.rs` / `src\decompiler.rs` / `potassium_tauri_lib::mcp`.

Full detection strategy in [`../docs/defense/DETECTION.md`](../docs/defense/DETECTION.md); developer hardening in [`../docs/defense/COUNTERMEASURES.md`](../docs/defense/COUNTERMEASURES.md).

## Open items

1. **Server-impact classification (primary, dynamic).** Reproduce the flood in an owned experience; measure whether server-side rate limiting and argument validation stop it.
2. **Downloaded injector / `Potassium.dll`.** Capture from an owned run; read the memory-write technique (manual map vs. `LoadLibrary`).
3. **Resource payload on the wire.** Capture the `/resource` and `/hashes` exchange to confirm payload encryption and validation.

## Scope and ethics

Static analysis of a legally obtained sample. No testing against live Roblox games or infrastructure. No payload, DLL, executor, or exploit code is reproduced; the downloaded executor components were not analysed. Mechanisms are documented for understanding, detection, and developer hardening only.
