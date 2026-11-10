# Architecture

How Potassium is built and how its parts fit together. Every factual statement in this document must trace to a finding in [`FINDINGS.md`](FINDINGS.md). Until the analysis produces those findings, the sections below are headings that describe what will be documented, not claims about the binary.

## Protection and anti-analysis

Potassium 1.6.0 ships as a single 28 MB executable built with Tauri: a Rust backend hosting a WebView2 user interface (P-01, P-05). It is unsigned (P-04).

Section entropy does not indicate packing or virtualization of the code (P-02, P-03). The perception that it is harder to analyze than Xeno comes from scale rather than protection: a large Rust binary with heavy inlining and an embedded web frontend. Integrity self-checks, anti-debugging, and any licensing layer are not yet examined.

The package holds no separate injectable DLL (P-08), so the component that runs inside the Roblox client is either embedded in the executable or obtained at runtime.

On disk, Potassium uses `%LOCALAPPDATA%\Potassium` with `workspace`, `autoexec`, and `scripts` folders (P-10).

## Attach mechanism

To be determined. How the loader places Potassium's code into or alongside the Roblox client, and whether it uses a conventional injection path or something closer to Xeno's bytecode-substitution approach.

## Execution model

The user-facing application exposes its functions as plain Tauri commands invoked by name; the command strings `attach`, `execute`, `autoexec`, `login`, and `update` are present (P-13). The named verbs are consistent with an executor flow (authenticate, attach to the client, run a script, run an autoexec script on attach, self-update), but the handlers behind them have not yet been read, so the wiring is inferred from the names rather than confirmed.

## Local control channels

Potassium exposes a local interface on `127.0.0.1` with a `/mcp` path, observed at address `127.0.0.1:8224` (P-14). A set of identifier strings (`mcp_enabled`, `mcp_status`, `mcp_servers`, `mcp_repl`, plus an adjacent port and state-manager reference) indicates a local MCP (Model Context Protocol) server, apparently for programmatic or AI-driven control of the executor (P-15). This, together with the `chat.potassium.pro` endpoint, points to an AI-integration capability that Xeno does not have. The request and response format of this channel is not yet mapped. `localhost:1420` also appears but is Tauri's default dev-server port and is treated as a build artifact.

## Resource handling

Potassium contacts `files.potassium.pro` as its update and resource-distribution channel, with route fragments `/version`, `/resource`, `/hashes`, and `/gui_name` (P-11, P-12). This parallels Xeno's remote version and resource channel: a version string, a downloadable resource bundle, and an integrity manifest of hashes. Authentication is handled against `api.potassium.pro/login`. Whether the fetched resource is encrypted, and how it is validated against `/hashes`, is not yet determined. The frontend assets themselves are a Vite/React bundle embedded in the executable (P-16).

## Server-impact capability

To be determined, and treated with the most care. The documented behavior is that Potassium can flood a RemoteEvent until the server process terminates. What this section must establish is the mechanism and, critically, the boundary condition: whether the shutdown depends on the target game leaving a remote unthrottled and unvalidated, or whether it occurs regardless. The distinction is developed in [`../defense/THREAT_ASSESSMENT.md`](../defense/THREAT_ASSESSMENT.md) and is not asserted in either direction until controlled measurement in a researcher-owned experience supports it.
