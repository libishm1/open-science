---
name: ai-debugging
description: Debugging procedure for AI coding agents working in native and managed code. Routes to three detailed playbooks - C and C++ (gdb, lldb, cdb, WinDbg, sanitizers, memory corruption, ABI and link errors), C# and .NET (Visual Studio, Rider, dotnet-dump, SOS, GC and async issues, assembly binding, bitness mismatches), and RhinoCommon and Grasshopper plugins (plugin load, components missing, geometry validity, threading, GH solve hangs). Use when a crash, exception, hang, wrong result or load failure needs reproducing and isolating, or when an agent must debug in a live debugger session.
license: see repository LICENSE
compatibility: Claude, Codex, local models, Ubuntu with ROS 2, Herdr and Omarchy. Use cdb or WinDbg on Windows, gdb or lldb on Linux and macOS. RhinoCommon steps need Windows or macOS.
---

# AI-assisted debugging

## Quick start (for small local models)

1. Write the symptom in one sentence, with the exact error text.
2. Find the matching reference in the routing table above. Read only that file.
3. Open the file's `## Contents` list. Pick one section. Read only that section with `Read`, using `offset` and `limit`.
4. Make the smallest test that reproduces the symptom. Save its output to a file.
5. Form one hypothesis. Test it. Record the result.
6. Fix one thing. Re-run the test. Stop when it passes.

Use this skill to run a debugging session with an agent. It sets the shared
procedure. The three references hold the platform detail.

## Route to a reference

| Symptom or environment | Read |
|---|---|
| Segfault, access violation, heap corruption, double free, use after free, sanitizer output, LNK2019, "undefined reference", ODR or ABI issue | `references/cpp-debugger.md` |
| NullReferenceException, "collection was modified", OutOfMemory, TypeLoad or MissingMethod, BadImageFormat (bitness), async deadlock, GC or finalizer stalls, binding redirects | `references/csharp-debugger.md` |
| Rhino or Grasshopper plugin (`.rhp`, `.gha`), RhinoCommon exception, invalid mesh or brep, component missing or throwing, GH solve hang, `GH_TaskCapableComponent` threading | `references/rhinocommon-debugger.md` |

A plugin that is C# on top of RhinoCommon usually needs both the C# reference
and the RhinoCommon reference. Start with the RhinoCommon reference for the
symptom, then the C# reference for the runtime question.

## The shared procedure

1. **State the symptom in one sentence.** Include the exact exception type,
   the exit code, or the wrong output. Record the environment: OS, bitness,
   runtime or compiler version, host application version.
2. **Reproduce minimally.** Cut the input, the code path and the setup until
   the failure still happens. Keep the smallest reproduction as a test or a
   script.
3. **Form one hypothesis and one test that can falsify it.** Prefer a
   breakpoint, a log line at a boundary, or a targeted assertion. Do not change
   two things at once.
4. **Capture evidence before changing code.** Stack trace, locals at the fault,
   loaded module list, the sanitizer report, or the minidump. Save it to a
   file. Do not rely on memory of what the debugger showed.
5. **Isolate the layer.** Application logic, library, runtime, native
   interop, host application, or environment. The layer decides the fix.
6. **Fix, then prove the fix.** Re-run the minimal reproduction. Run the
   regression suite. For UI or geometry output, check the output in the host
   application, because a passing test does not prove the picture is right.
7. **Record the root cause.** One short note: symptom, cause, fix, and the
   check that proves it. Add a regression test where the platform allows.

## Rules for agents

- Debug in the environment where the failure occurs. Do not substitute a
  simpler environment and claim the bug is gone.
- Do not run a debugger attach, a process kill or a host-application launch
  without the user's go-ahead, unless the user has granted that permission for
  the session. Name the process before killing it.
- Never kill a process by image name when several instances may be running.
  Identify the process ID first.
- Mark every version-sensitive command as `verify:` and confirm it with the
  tool's `--help` or the official documentation before relying on it.
- Say what was not verified. A debugging claim without a reproduction or a
  captured trace is a hypothesis.

## Output of a debugging session

- Symptom, environment, and minimal reproduction (path or script).
- Evidence captured, with file names.
- Hypotheses tested, with result for each.
- Root cause, fix, and proof.
- Open risks and what would confirm them.

## Platforms and orchestrators

This skill runs on Claude, Codex, local models, Herdr and Omarchy. Read
`references/platform-compatibility.md` for which steps need which operating system, how to
name paths, and how to give each agent pane its inputs.
