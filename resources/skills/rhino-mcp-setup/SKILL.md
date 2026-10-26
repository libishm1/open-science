---
name: rhino-mcp-setup
description: Procedure for connecting an AI agent to a running Rhino 8 through MCP, starting the session, verifying the slot, and deploying Grasshopper plugins safely (load guards, duplicate-copy checks, restart rules). Use when an agent must drive Rhino or Grasshopper, deploy a .gha plugin, or diagnose why a plugin or slot does not load. Windows or macOS only.
compatibility: Claude, Codex, local models, Herdr and Omarchy as clients. Rhino 8 and Grasshopper run on Windows or macOS. Ubuntu can drive a remote Rhino host.
license: see repository LICENSE
---

# Rhino MCP setup and plugin deployment

## Quick start (for small local models)

1. Start Rhino with the plugin loaded. Run the plugin's start command (for example `MCPStart`). Accept the default port.
2. In the agent, list the slots. If your slot is missing, stop. Do not make a call without a slot.
3. Test one script call that returns a value on standard output.
4. Before you deploy a plugin, check which libraries are loaded. Do not scan the libraries again if any are loaded.
5. After a deploy, restart Rhino before you judge the fix.

Procedure only. Apply it to your own plugins, definitions, and fixtures. Keep results and findings out of shared files.

## 1. Drive a live Rhino through MCP

- Run one MCP server for scripts inside Rhino (the official router) and one bridge for the
  Grasshopper canvas. Do not mix them up.
- Check which Python the script host runs. Use the host's document object, not a global.
  Results come back on standard output.
- Activate the session with the plugin's start command in Rhino. A dialog that only shows
  configuration does not start anything. Confirm the slot appears in the slot list before the
  first call.
- Never make a call without a slot to force one open. A slot-less call can launch a clean Rhino
  with none of your plugins loaded.
- After you change the MCP configuration, restart the agent client. Do not expect a new server to
  appear in the running session.

## 2. Load and deploy plugins safely

- Before a fix counts as failed, restart Rhino. The process keeps the old assembly in memory.
  Disabling a component or a solver does not unload it.
- Check what is loaded, not what is on disk: list the loaded libraries and look up the component
  GUID through the component server.
- Load guard. Call the library scan only when the library count is zero. Scanning again while
  libraries are loaded re-registers every component and causes ID conflicts. On a normal
  relaunch, do nothing.
- Keep one copy of each plugin in the scanned folders. Scanning is recursive, so a duplicate loads
  twice and fails with ID conflicts.
- Disable third-party plugins that break wiring. Disable every copy: the library copy and any
  package-manager copy.
- Confirm the deployed file's size and modification time after each copy. Ask for a full restart
  before you conclude a fix failed.
- Deploy with a command that is not piped into a tool that stops early. An early stop can kill the
  child process mid-copy. Verify the file afterwards.

## Files

- `references/platform-compatibility.md` - where each step runs.
