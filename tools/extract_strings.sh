#!/usr/bin/env bash
# Static string extraction and categorized grep passes used for Phase 1-3.
# Usage: extract_strings.sh <path-to-Potassium.exe>
# Reads only; nothing is executed and nothing is fetched over the network.
set -euo pipefail

S="${1:?usage: extract_strings.sh <exe>}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

strings -n 5 "$S" > "$WORK/ascii.txt"
strings -n 6 -e l "$S" > "$WORK/utf16.txt"
A="$WORK/ascii.txt"

echo "=== frontend asset filenames ==="
grep -aoiE "[a-z0-9_/-]+\.(js|mjs|css|html|wasm|map|svg|png|woff2?)" "$A" "$WORK/utf16.txt" \
  | sed 's/^[^:]*://' | sort -u

echo "=== Tauri IPC / plugin command surface ==="
grep -aoiE "__TAURI[A-Z_]*|plugin:[a-z0-9_-]+\|[a-z0-9_]+|tauri://[a-z0-9._/-]+" "$A" | sort -u

echo "=== distinct plugin namespaces ==="
grep -aoiE "plugin:[a-z0-9_-]+\|" "$A" | sort | uniq -c | sort -rn

echo "=== network endpoints ==="
grep -aoiE "https?://[a-z0-9.:/_-]{6,}|wss?://[a-z0-9.:/_-]{6,}" "$A" | sort -u

echo "=== potassium.pro endpoints and file routes ==="
grep -aoiE "https?://[a-z0-9.]*potassium\.pro[a-z0-9./_-]*" "$A" | sort -u
grep -aoE "files\.potassium\.pro/[a-z0-9_]+" "$A" | sort -u

echo "=== local server: 127.0.0.1 / ports / mcp ==="
grep -aoE "127\.0\.0\.1:[0-9]{2,5}|localhost:[0-9]{2,5}|/mcp[a-z0-9_/]*|mcp_[a-z]+|ws://127[0-9:./]+" "$A" \
  | sort | uniq -c | sort -rn

echo "=== candidate command names ==="
grep -aoE "\b(execute|inject|attach|autoexec|login|logout|update|execute_script|read_console|list_clients|clear_console|run_script)\b" "$A" \
  | sort | uniq -c | sort -rn

echo "=== internal Rust module paths ==="
grep -aoE "src\\\\[a-z0-9_\\\\]+\.rs" "$A" | sort | uniq -c | sort -rn

echo "=== crate SBOM (name-version) ==="
grep -aoE "index\.crates\.io-[a-f0-9]+\\\\[a-z0-9_-]+-[0-9]+\.[0-9]+\.[0-9]+" "$A" \
  | sed -E 's/.*\\//' | sort -u

echo "=== MCP / JSON-RPC protocol methods ==="
grep -aoE "\"(tools/list|tools/call|initialize|resources/list|prompts/list|ping|notifications/[a-z]+)\"|jsonrpc" "$A" \
  | sort | uniq -c | sort -rn

echo "=== MCP tool context (schema / descriptions) ==="
grep -aoE ".{0,40}(execute_script|read_console|list_clients).{0,120}" "$A" | sort -u
