---
name: cpp-debugger
description: This skill should be used when the user is debugging C or C++ code in an interactive debugger session (gdb, lldb, MSVC cdb, WinDbg, Visual Studio Debugger), investigating segfaults / SIGSEGV / access violations / EXCEPTION_ACCESS_VIOLATION, heap corruption, double-free, use-after-free, dangling reference, iterator invalidation, object slicing, ODR violations, ABI mismatches, link errors (LNK2019, "undefined reference to"), template error spam, or interpreting sanitizer output (AddressSanitizer / UBSan / ThreadSanitizer / MemorySanitizer) and memory leak reports (Valgrind, Dr. Memory). Use it whenever the user shares a stack trace, core dump, .dmp / .mdmp file, asks "why is this crashing", talks about pointer or memory corruption in C++, or works on native interop / P/Invoke from the native side.
---

# C++ Debugger

Procedural guide for debugging C and C++ programs across Windows, Linux, and macOS. Optimized for native interop work (P/Invoke targets, COM, Rhino C++ SDK plugins, etc.).

## When to use

Use this skill when:

- The user is in or about to start an interactive debugger for native code: `gdb`, `lldb`, `cdb`, `windbg`, or the Visual Studio debugger.
- A C or C++ program crashes with: SIGSEGV, SIGABRT, SIGBUS, SIGFPE, EXCEPTION_ACCESS_VIOLATION, STATUS_HEAP_CORRUPTION, STATUS_STACK_BUFFER_OVERRUN.
- The output mentions AddressSanitizer (`==ERROR: AddressSanitizer:`), UBSan (`runtime error:`), TSan (`WARNING: ThreadSanitizer:`), MSan, Valgrind (`Invalid read of size`, `definitely lost`), or Dr. Memory.
- Symptoms point to: use-after-free, double-free, heap-buffer-overflow, stack-buffer-overflow, uninitialized read, race condition, deadlock, memory leak, iterator invalidation, slicing, dangling reference, virtual call during construction or destruction, ODR violation.
- Link errors: `LNK2019: unresolved external symbol`, `LNK1120`, `undefined reference to`, `multiple definition of`, `DSO missing from command line`.
- Template / concept / SFINAE error walls (hundreds of lines starting with `In file included from`).
- ABI mismatch hints: mismatched runtime libraries (`/MT` vs `/MD`), name-mangling differences, `std::string` ABI flips between GCC 4 and 5+ (`_GLIBCXX_USE_CXX11_ABI`).

## When NOT to use

- Code is C# / .NET — use the `csharp-debugger` skill.
- Code is Rust, Go, Java, Python, or another non-native language. Different debuggers and idioms apply.
- The user is debugging build configuration only (CMake, MSBuild, makefiles) without a runtime symptom — handle as a build issue, not a debugger session.
- The user wants a code review or refactoring without a reproducible failure.

## Sourcing current docs (Context7 + official primary sources)

Do not invent debugger flags, sanitizer options, or platform-specific behavior. Look them up.

**Context7 MCP, when available**, is the first stop for any flag, command, or API. Resolve a library id with `mcp__context7__resolve-library-id`, then fetch the topic-scoped doc with `mcp__context7__get-library-docs`. Library names worth knowing for this skill:

- `microsoft/visualstudio-debugger` — Visual Studio Debugger.
- `microsoft/windows-driver-kit` and `microsoft/windbg` — WinDbg / cdb / kd, Time Travel Debugging.
- `microsoft/MSVC` and `microsoft/cpp-docs` — `cl.exe`, `link.exe`, `/RTC1`, `/sdl`, `/GS`, `/guard:cf`, runtime libraries (`/MT` vs `/MD`).
- `gnu/gdb`, `llvm/lldb`, `google/sanitizers` — gdb, lldb, ASan / UBSan / TSan / MSan / LSan.
- `valgrind/valgrind` — Memcheck, Helgrind, DRD, Callgrind.

**Microsoft Learn is the canonical primary source** for everything Microsoft-owned. Prefer these URLs over blog posts and Stack Overflow when Context7 is offline:

- Visual Studio Debugger: `https://learn.microsoft.com/visualstudio/debugger/`
- MSVC compiler options: `https://learn.microsoft.com/cpp/build/reference/compiler-options`
- MSVC runtime checks: `https://learn.microsoft.com/cpp/build/reference/rtc-run-time-error-checks`
- C++ standard library debug iterators: `https://learn.microsoft.com/cpp/standard-library/iterator-debug-level`
- WinDbg / cdb / kd reference: `https://learn.microsoft.com/windows-hardware/drivers/debugger/`
- Crash dump generation: `https://learn.microsoft.com/windows/win32/wer/collecting-user-mode-dumps`
- Time Travel Debugging: `https://learn.microsoft.com/windows-hardware/drivers/debuggercmds/time-travel-debugging-overview`
- AppVerifier and PageHeap (`gflags`): `https://learn.microsoft.com/windows-hardware/drivers/devtest/application-verifier`

**Non-Microsoft tools — use the official upstream docs:**

- gdb: `https://sourceware.org/gdb/current/onlinedocs/gdb/`
- lldb: `https://lldb.llvm.org/`
- AddressSanitizer / UBSan / TSan / MSan: `https://clang.llvm.org/docs/AddressSanitizer.html` and the matching pages under `/docs/` in the same tree.
- Valgrind: `https://valgrind.org/docs/manual/manual.html`
- Dr. Memory: `https://drmemory.org/docs/`

**Rule when sources disagree:** the tool's own help (`gdb --help`, `cl.exe /?`, `dumpbin /?`, `windbg /?`) is final. Microsoft Learn and Context7 are second. Mark anything else as "verify with `<command> --help`" rather than asserting it.

## Workflow

### 1. Reproduce minimally

Before opening a debugger, get a deterministic repro.

- Pin the inputs that cause the crash. If the bug is intermittent, run in a loop: `while ./repro; do :; done` (bash) or `while ($true) { .\repro.exe; if (-not $?) { break } }` (PowerShell).
- Build with debug info. Never debug an optimized release binary unless the bug only repros under `-O2` / `/O2`.
  - GCC / Clang: `-g -O0 -fno-omit-frame-pointer`
  - MSVC: `/Zi /Od /DEBUG`
- Strip third-party noise: comment out unrelated subsystems until the smallest failing program remains.

### 2. Choose the debugger

Match the toolchain, not personal preference:

| Platform / build | Debugger |
|---|---|
| MSVC (cl.exe), Windows app or DLL | Visual Studio debugger, `cdb`, or `windbg` |
| MinGW / Clang on Windows | `gdb` (from the same toolchain) or `lldb` |
| Linux (GCC / Clang) | `gdb`, `lldb` |
| macOS (Clang / Apple Clang) | `lldb` (default; `gdb` requires codesigning) |
| Cross-compiled / embedded | `gdb-multiarch` over `gdbserver` |

If the user is already in a different debugger, stay there. Do not force a switch.

### 3. Pick attach vs launch

- **Launch fresh** when the bug fires near startup, when you need to break on `main`, or when env vars / args matter.
- **Attach to a running process** when the bug only happens after long-running setup, or when the program is a service / plugin host (e.g. attaching to `Rhino.exe` for a C++ Rhino plugin).
  - gdb: `gdb -p <pid>`
  - lldb: `lldb -p <pid>`
  - Visual Studio: Debug -> Attach to Process -> select `Rhino.exe`, code type "Native".
  - cdb / windbg: `cdb -p <pid>` or `windbg -p <pid>`.
- **Post-mortem from a core / dump** when the process already crashed:
  - Linux core: `gdb ./mybin core` (ensure `ulimit -c unlimited` was set before the crash and check `/proc/sys/kernel/core_pattern`).
  - macOS core: `lldb -c /cores/core.<pid> ./mybin` (cores require `ulimit -c unlimited` and may be disabled by default).
  - Windows minidump: open the `.dmp` in Visual Studio (File -> Open -> select dump), or `windbg -z crash.dmp`.

### 4. Turn on diagnostics before the next run

Sanitizers and runtime checks catch bugs the debugger alone misses.

GCC / Clang:

```bash
# Address + undefined behavior. Cheap, catches most C/C++ memory bugs.
clang++ -g -O1 -fno-omit-frame-pointer -fsanitize=address,undefined source.cpp -o repro

# Thread sanitizer (separate build, incompatible with ASan).
clang++ -g -O1 -fsanitize=thread source.cpp -o repro_tsan

# Memory sanitizer (uninitialized reads). Clang only, Linux only.
clang++ -g -O1 -fsanitize=memory -fno-omit-frame-pointer source.cpp -o repro_msan
```

Make ASan output more useful at runtime:

```bash
ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:halt_on_error=1:print_stacktrace=1
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
LSAN_OPTIONS=verbosity=1:log_threads=1
```

libstdc++ / libc++ debug iterators:

```bash
# GCC libstdc++: bounds-check std::vector etc., catches iterator invalidation.
g++ -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC source.cpp

# libc++:
clang++ -D_LIBCPP_ENABLE_DEBUG_MODE=1 source.cpp
```

MSVC (cl.exe) extra checks:

```
/RTC1     Stack frame and uninitialized variable checks (Debug builds).
/sdl      Additional security checks; treats some warnings as errors.
/GS       Buffer security checks (default in modern MSVC).
/guard:cf Control Flow Guard.
```

In code, before including STL:

```cpp
// MSVC STL: 0 = release, 1 = release + checks, 2 = full debug iterators.
#define _ITERATOR_DEBUG_LEVEL 2
```

Valgrind (Linux / macOS, no recompile required):

```bash
valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./repro
valgrind --tool=helgrind ./repro      # data races
valgrind --tool=drd ./repro           # alternate race detector
```

Dr. Memory (Windows / Linux):

```
drmemory.exe -- repro.exe arg1 arg2
```

### 5. Drive the debugger

Use the cheatsheet below. Then form a hypothesis, set a breakpoint or watchpoint, and step.

## gdb / lldb cheatsheet

Both debuggers accept similar commands. lldb command shown after `|`.

```
# Run / attach
run [args]                       | run
attach <pid>                     | process attach -p <pid>
target remote host:port          | gdb-remote host:port

# Stack
backtrace                  / bt  | thread backtrace                / bt
backtrace full                   | thread backtrace -f
frame <n>                  / f n | frame select <n>                / f n
up / down                        | up / down
info args / info locals          | frame variable

# Breakpoints
break main                 / b main             | breakpoint set --name main / b main
break file.cpp:42                                | breakpoint set --file file.cpp --line 42
break ns::Class::method                          | breakpoint set --method method (or --name)
break file.cpp:42 if i == 100                    | breakpoint set --file file.cpp --line 42 --condition "i==100"
rbreak ^MyNamespace::                            | breakpoint set --func-regex "^MyNamespace::"
info breakpoints           / i b                 | breakpoint list
delete <id>                                      | breakpoint delete <id>

# Watchpoints (break when memory changes)
watch *((int*)0x7ffe0000)                        | watchpoint set expression -- *((int*)0x7ffe0000)
watch myVar                                      | watchpoint set variable myVar
rwatch myVar    (read)                           | watchpoint set variable -w read myVar
awatch myVar    (read or write)                  | watchpoint set variable -w read_write myVar

# Stepping
next                       / n   | thread step-over               / n
step                       / s   | thread step-in                 / s
finish                           | thread step-out
continue                   / c   | process continue               / c
stepi / nexti                    | thread step-inst / step-inst-over

# Printing
print expr                 / p   | expression -- expr             / p expr
print/x var       (hex)          | expression -f x -- var
display var       (auto-print)   | target stop-hook add ...   (or just `frame variable`)
ptype expr        (type)         | type lookup expr                / image lookup -t TypeName
x/16xb 0x...      (raw memory)   | memory read --size 1 --format x --count 16 0x...

# Threads
info threads               / i t | thread list
thread <n>                 / t n | thread select <n>
thread apply all bt              | thread backtrace all

# Signals
handle SIGPIPE nostop noprint    | process handle SIGPIPE -s false -p false
catch throw                      | breakpoint set -E c++

# Symbols / sharedlibs
info sharedlibrary               | image list
sharedlibrary <name>             | image lookup -n <name>
```

### STL pretty-printers

- gdb on Linux loads libstdc++ pretty-printers automatically. If they are missing, `set print pretty on` and check `info pretty-printer`.
- lldb auto-formats `std::string`, `std::vector`, `std::map`, `std::shared_ptr`. Use `frame variable v` (not `print v`) for the prettiest output.
- Visual Studio uses `.natvis` files. STL containers display correctly out of the box. For your own types, ship a `MyType.natvis` next to the project.

## WinDbg / cdb cheatsheet

For Windows minidump and live-attach work.

```
# Load symbols (do this first or nothing works)
.symfix+ <repo-path>
.sympath+ srv*<repo-path>
.reload /f

# Where am I
k                  Stack trace.
kb                 Stack trace with first 3 args.
kn                 Stack trace with frame numbers.
~                  List threads.
~*k                Stack trace, every thread.
~<n>s              Switch to thread n.

# Frames and locals
.frame /r <n>      Switch frame, dump registers.
dv                 Dump local variables.
dt this            Display this pointer as a struct.
dt <type> <addr>   Display memory at addr as <type>.

# Memory
db / dw / dd / dq <addr>      Bytes / words / dwords / qwords.
!address <addr>               Describe a memory region.
!analyze -v                   Auto-triage a crash dump. Run this first on a .dmp.
!heap -p -a <addr>            Trace heap block back to its allocation.
!verifier                     If Application Verifier is on, dump its findings.

# Breakpoints (live debug only)
bp module!Namespace::Class::Method
bm module!*Pattern*           Set on every match.
bl                            List.
bc *                          Clear all.

# Exception handling
sxe av                        Stop on access violation (first chance).
sxd av                        Skip first-chance, only stop on second-chance.
```

For a crashed `.dmp`, the universal opener is:

```
windbg -z crash.dmp
.symfix
.reload
!analyze -v
```

## Common bug patterns

### Use-after-free

Symptoms: random crashes, garbage values, ASan `heap-use-after-free`, occasional success.

Steps:

1. Build with `-fsanitize=address`. ASan prints both the freeing stack and the use stack.
2. If ASan is unavailable, set a watchpoint on the freed pointer's storage location to catch any later access.
3. In WinDbg, enable PageHeap for the binary so freed blocks become inaccessible immediately:
   `gflags.exe /p /enable myapp.exe /full`. Run, then reproduce. The next use-after-free becomes an immediate access violation.
4. Audit ownership: who owns the lifetime? Replace raw pointers with `std::unique_ptr` / `std::shared_ptr` once the bug is understood.

### Double-free

Symptoms: `free(): double free detected in tcache 2`, `_CrtIsValidHeapPointer` assertion, ASan `attempting double-free`.

Steps:

1. ASan reports both `free` stacks. The second one is the bug.
2. Look for: copy of an owning pointer, missing rule of three / five, manual `delete` on a `unique_ptr.get()`.
3. Add `=delete` to the copy constructor of any class that owns a raw resource until you decide the right semantics.

### Heap-buffer-overflow / stack-buffer-overflow

Symptoms: ASan `heap-buffer-overflow`, `___stack_chk_fail` (canary), `STATUS_STACK_BUFFER_OVERRUN`.

Steps:

1. ASan / `/GS` already point at the offending write. Read the report top-to-bottom.
2. If only Valgrind is available: `valgrind --tool=memcheck` will flag the invalid write.
3. Common cause: off-by-one in a `for` loop, `strcpy` / `sprintf` without bounds, indexing with a signed int that went negative.

### Iterator invalidation

Symptoms: crash inside `std::vector::operator[]`, garbage data, intermittent.

Steps:

1. Rebuild with `-D_GLIBCXX_DEBUG` (libstdc++) or `_ITERATOR_DEBUG_LEVEL=2` (MSVC). The next run aborts at the exact invalid use.
2. Look for: `push_back` / `insert` / `erase` inside a range-based for, holding an iterator across reallocation, erasing without `it = c.erase(it)`.

### Object slicing

Symptoms: virtual function calls invoke the base class implementation; subclass state is missing.

Steps:

1. Find every place a derived object is passed or stored by value (`Base b = derived;` or `vector<Base>` containing `Derived` instances).
2. Switch storage to `vector<unique_ptr<Base>>` or pass by reference / pointer.

### Dangling reference / pointer to local

Symptoms: works in debug, fails in release; values change between calls.

Steps:

1. Compile with `-Wreturn-stack-address -Wdangling-gsl` (Clang) or `/W4 /WX` (MSVC). Many of these are caught at compile time today.
2. ASan with `--detect_stack_use_after_return=1` finds it at runtime.

### ODR violation

Symptoms: same type defined differently in two TUs, random crashes after refactor, mismatched `sizeof` in different files.

Steps:

1. ASan with `-fsanitize=address -fno-sanitize=vptr` on Linux often catches it (`ODR violation`).
2. Search for: a class defined in a header that includes private members guarded by a macro (e.g., `#ifdef DEBUG`), where some TUs see the macro and others do not.

### Race condition

Symptoms: works on one thread, intermittent on many; tools like Helgrind / TSan complain.

Steps:

1. Build with `-fsanitize=thread`. Re-run. TSan dumps two stacks: the conflicting accesses.
2. Identify the shared mutable state. Either lock it (`std::mutex` + `std::lock_guard`), make it atomic (`std::atomic<T>`), or remove the sharing.
3. Avoid `volatile` for thread synchronization. It is not a memory barrier in C++.

### Deadlock

Symptoms: process hangs, all threads waiting.

Steps:

1. Attach to the running process. `thread apply all bt` (gdb) / `~*k` (WinDbg) / Debug -> Windows -> Parallel Stacks (VS).
2. Find threads parked in `pthread_cond_wait`, `WaitForSingleObject`, `std::mutex::lock`. Note which lock each thread already holds and which it is asking for. The cycle is the deadlock.
3. Fix by enforcing a global lock acquisition order, or use `std::lock(a, b)` to acquire multiple mutexes deadlock-free.

### Memory leak

Symptoms: RSS grows over time; Valgrind `definitely lost`; ASan `LeakSanitizer`.

Steps:

1. Run under LSan (part of ASan) or `valgrind --leak-check=full --show-leak-kinds=all`.
2. Each report includes the allocation stack. Walk it back to the owner.
3. For long-running processes, take two `gcore` / `procdump` snapshots and diff heap usage.

### Integer overflow / signed UB

Symptoms: bizarre array indices, infinite loops, `runtime error: signed integer overflow` from UBSan.

Steps:

1. Build with `-fsanitize=undefined`. UBSan pinpoints the line.
2. Move the arithmetic to unsigned types only when wrap-around is intended; otherwise add a bounds check.

## Linker error triage

`LNK2019` / `undefined reference to`:

1. The symbol is declared but never defined, or defined in a TU not linked.
2. Demangle the symbol: `c++filt _ZN...` (GNU) or paste into https://demangler.com.
3. Check for: missing `.cpp` in the build, missing `extern "C"` on a C symbol called from C++, mismatched template instantiation, `inline` function defined in `.cpp` instead of header, missing library on the link line.

`multiple definition of`:

1. A non-inline function or variable is defined in a header included by multiple TUs. Add `inline` (C++17 also for variables) or move the definition to a single `.cpp`.

ABI / runtime mismatches on Windows:

- All linked binaries must agree on `/MT` vs `/MD` (static vs dynamic CRT). Mismatch crashes deep in CRT.
- Debug (`/MDd`) and release (`/MD`) cannot be mixed.

ABI / runtime mismatches on Linux:

- `_GLIBCXX_USE_CXX11_ABI=0` vs `=1` produces incompatible `std::string` and `std::list`. All libraries must agree.

## Template error spam

When the compiler dumps a 600-line wall:

1. Read top-down to the first `error:` line. Everything below is consequence.
2. The note immediately above the error usually shows the failing constraint or substitution.
3. Add `static_assert(std::is_same_v<T, ExpectedType>, "...")` near the call site to confirm the actual type.
4. With Clang, add `-fdiagnostics-show-template-tree -ftemplate-backtrace-limit=0` for legible output.
5. With C++20 concepts, replace SFINAE with `requires` clauses; the error becomes one line.

## Quick decision tree

```
Crash?
  Got a core / dump?            -> post-mortem (gdb core / windbg -z .dmp / VS open dump)
  Reproducible live?            -> launch under debugger with sanitizers
  Only on release?              -> rebuild release with -g -O2, run under ASan with -O1

Hang?
  Attach to running process, dump all thread stacks, look for lock cycles.

Wrong answer, no crash?
  Watchpoint on the suspect variable, or printf-style with logging,
  or rr (Linux) for reverse execution.

Sanitizer report?
  Read the FIRST report only. Fix it. Rerun. Sanitizers cascade.

Link error?
  Demangle, search build for the symbol, check link line and lib search path.
```

## Reverse / time-travel debugging

When stepping forward keeps missing the corruption:

- Linux: `rr record ./repro` then `rr replay`. Inside, `reverse-continue`, `reverse-next`, `reverse-finish` work. Set a watchpoint and `reverse-continue` to find what set the value.
- Windows: WinDbg Time Travel Debugging. Record with `ttd.exe -out trace.run repro.exe` (verify: `ttd.exe /?`), then `windbg trace.run`. Use `!tt 0`, `!positions`, `g-` to go backward.

## Working with native interop / P/Invoke

When debugging a native DLL called from .NET:

1. In Visual Studio, set the project debugger type to "Mixed (Managed and Native)" so both stacks are visible.
2. Crashes inside the native DLL still surface in the .NET process. Attach to the host (e.g. `Rhino.exe`, `dotnet.exe`) with code type "Native" and "Managed".
3. Calling-convention mismatch (`__stdcall` vs `__cdecl` on x86) corrupts the stack at return. On x64 there is one calling convention so this class of bug disappears.
4. Marshalling: arrays passed as `IntPtr` must be pinned on the managed side; `[DllImport]` `CharSet` must match the C function signature (`A` vs `W`).
5. Build the C++ side with `/Zi` and ship the `.pdb` next to the DLL so the debugger can resolve symbols.
