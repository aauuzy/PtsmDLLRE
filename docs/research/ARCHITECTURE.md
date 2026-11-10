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

To be determined. How script is submitted, scheduled, and run, and what local interface the user-facing application uses to drive it.

## Local control channels

To be determined. Any localhost server, named pipe, shared memory, or file-based channel between the application and the injected component, including the request and response format.

## Resource handling

To be determined. Embedded scripts and data, any encryption or compression over them, and any remote endpoints the sample contacts for updates or payloads.

## Server-impact capability

To be determined, and treated with the most care. The documented behavior is that Potassium can flood a RemoteEvent until the server process terminates. What this section must establish is the mechanism and, critically, the boundary condition: whether the shutdown depends on the target game leaving a remote unthrottled and unvalidated, or whether it occurs regardless. The distinction is developed in [`../defense/THREAT_ASSESSMENT.md`](../defense/THREAT_ASSESSMENT.md) and is not asserted in either direction until controlled measurement in a researcher-owned experience supports it.
