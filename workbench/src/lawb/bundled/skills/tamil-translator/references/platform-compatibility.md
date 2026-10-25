# Platform compatibility (Claude, Codex, local agents, Herdr, Omarchy)

Read this with the skill's `SKILL.md`. It states where each step runs. It does not promise that
a tool works on your machine. Check the versions you install.

## Where each step runs

| Step type | Windows | macOS | Linux (including Omarchy) |
|---|---|---|---|
| Python, pandas, IFC, Topologic, scripts in the skill | yes | yes | yes |
| Rhino and Grasshopper (RhinoCommon, GhPython) | yes | yes | no. Rhino is not built for Linux. Use Windows or macOS, or a remote Rhino host |
| Visual Studio and cdb or WinDbg debugging | yes | no | no |
| gdb, lldb, sanitizers, dotnet-dump | yes (MinGW, WSL, dotnet) | yes | yes |
| Document export (LaTeX, pandoc) | yes | yes | yes |

Write paths with environment variables or relative paths (`$HOME`, `%USERPROFILE%`,
`<project-dir>`). Do not hard-code a machine's drive or user folder.

## Agent hosts

| Host | How it reads a skill | Notes |
|---|---|---|
| Claude (claude.ai, Claude Code) | Copy the skill folder to a skills directory, or load `SKILL.md` by name | Trigger on the `description` line |
| Codex | Point the prompt at `SKILL.md`; load `references/` on demand | Reads `AGENTS.md` at the repo root |
| Local models (Qwen, Llama and others) | Load `SKILL.md` alone first; add one reference per task | Keep context small |
| Herdr | Run one agent per pane. Give the pane's agent the skill path and the task card | See below |
| Omarchy | Same as Linux. Install the agent CLI, then copy skills to `~/.claude/skills/` or the Codex skills folder | Hyprland desktop; no change to skill content |

## Herdr (terminal workspace manager for coding agents)

Source: the README of `herdrdev/herdr` (Apache-2.0), read 2026-10-24. Herdr describes itself
as "the runtime your coding agents live on". It keeps terminals running in a background server
when the client closes, marks each pane as working, blocked or idle, and lets agents drive it
through a CLI and socket API (spawn panes, prompt other agents, wait until an agent is blocked).
It runs the agents' own terminals; it does not replace them. Use the skills like this:

1. Install Herdr from the official repository: `brew install herdr`, `mise use -g herdr`, or the
   install script in the README. Windows support is a beta with an endpoint-protected install.
2. Read the agents page and the socket API docs at herdr.dev/docs for the agent you use, and
   for the agent skill Herdr provides.
3. Give each pane the task card and the skill path. One skill per pane keeps the context small.
4. Use the research-synthesis or ai-debugging skill for the coordinating pane. Use the
   computational-design skill for the pane that edits models or code.

The README does not document a multi-agent orchestration workflow. Any coordination logic lives
in your task cards and in the file contract of the Agent-orchestration repository
(`docs/EXTERNAL_ORCHESTRATORS.md`). Verify the exact CLI commands against
your installed version before you script them.

## Ubuntu and ROS 2 (robotics)

ROS 2 is the robotics default for this work. Pair the Ubuntu release with the ROS 2 distribution
it supports. Verify the pairing against the ROS 2 documentation for the version you install.
Humble targets Ubuntu 22.04 and Jazzy targets Ubuntu 24.04.

| Step | Ubuntu + ROS 2 | Notes |
|---|---|---|
| Python skill scripts and IFC, Topologic, GraphML | yes | Use a virtualenv. Keep ROS Python separate from the rest |
| ROS 2 nodes, `colcon` builds, `ros2` CLI | yes | Required for the UR10e and ROS 2 stack |
| UR10e driver and URScript | yes | Simulate first (Level 2). No hardware commands without an explicit gate |
| Rhino and Grasshopper | no | Run on Windows or macOS, or on a remote Rhino host. Pass poses through files or a bridge |
| gdb, `rr`, sanitizers, `ros2 bag` | yes | Use gdb or rr for C++ nodes. Record bags for replay |
| cdb, WinDbg, Visual Studio | no | Use the Windows host for these |

Robotics rules that apply to every skill on this platform (from the repository rules):

- Never mix TCP poses with motion poses. Check units (mm vs m), frames, and rotation
  conventions before passing a pose between tools.
- Level 1 is offline code generation. Level 2 is simulation. Level 3 needs an explicit
  hardware flag. Do not run Level 3 from a skill.
- Record the ROS 2 distribution, Ubuntu release, and driver version in every experiment.

## Omarchy (Arch Linux with Hyprland)

Omarchy is an opinionated Arch Linux setup with the Hyprland compositor. Skills need no
changes on Omarchy. Two points to remember:

- Rhino and Grasshopper steps run on a separate Windows or macOS machine, or on a remote host.
- Use Linux paths and line endings (LF). Debugging skills should use gdb or lldb, not cdb.

## Versions

Record the version of each tool you use. This document was written on 2026-10-24 from public
descriptions of Omarchy and Herdr. Re-check both against their official sources before you rely
on a specific command or setting.
