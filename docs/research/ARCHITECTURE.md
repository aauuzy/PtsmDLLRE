# Architecture

How Potassium is built and how its parts fit together. Every factual statement in this document must trace to a finding in [`FINDINGS.md`](FINDINGS.md). Until the analysis produces those findings, the sections below are headings that describe what will be documented, not claims about the binary.

## Protection and anti-analysis

To be determined. The sample is reported to be harder to unpack than Xeno, so this is the first thing characterized: packing or virtualization, section entropy, integrity self-checks, anti-debugging, and any licensing or hardware-binding layer. Nothing downstream can be trusted until the protection is understood and, where necessary, unwrapped for static reading.

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
