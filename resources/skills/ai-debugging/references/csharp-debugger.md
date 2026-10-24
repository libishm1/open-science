---
name: csharp-debugger
description: This skill should be used when the user is debugging C# / .NET code in an interactive debugger session (Visual Studio, VS Code C# Dev Kit, Rider, WinDbg + SOS, dotnet-dump), or hits exceptions like NullReferenceException, InvalidOperationException ("Collection was modified"), OutOfMemoryException, TypeLoadException, FileNotFoundException at assembly load, MissingMethodException, BadImageFormatException (x86/x64 mismatch), TargetInvocationException, or async / Task / await issues (UI-thread deadlocks from .Result or .Wait(), ConfigureAwait misuse, ValueTask continuation problems). Also use when investigating GC / memory pressure, large object heap fragmentation, finalizer queue stalls, IDisposable leaks, P/Invoke crashes from the managed side, .NET Framework 4.8 vs .NET 6+ runtime drift, or assembly binding / AssemblyLoadContext / binding-redirect problems. Strongly applies to Rhino / Grasshopper plugin debugging where Claude must attach to Rhino.exe, inspect GH_TaskCapableComponent async paths, or diagnose threading bugs on Rhino's UI thread.
---

# C# Debugger

Procedural guide for debugging C# and .NET code. Covers .NET Framework 4.8 (Windows-only, used for Rhino / Grasshopper plugins) and modern .NET 6+ on Windows / Linux / macOS.

## When to use

Use this skill when:

- The user is in or about to start a managed debugger: Visual Studio, VS Code with C# Dev Kit / OmniSharp, Rider, `dotnet-dump analyze`, `dotnet-trace`, `dotnet-counters`, WinDbg + SOS.
- A .NET program throws or surfaces:
  - `System.NullReferenceException`, `System.ArgumentNullException` after a chain of calls.
  - `System.InvalidOperationException: Collection was modified; enumeration operation may not execute`.
  - `System.OutOfMemoryException`, `Insufficient memory to continue the execution of the program`.
  - `System.TypeLoadException`, `System.IO.FileNotFoundException` at assembly load.
  - `System.BadImageFormatException` (an x86 process trying to load an x64 assembly or vice versa).
  - `System.MissingMethodException` / `System.MissingFieldException` after a binding-redirect drift or NuGet upgrade.
  - `System.Reflection.TargetInvocationException` wrapping a real cause.
  - `System.Threading.Tasks.TaskCanceledException`, `AggregateException`.
- Symptoms include: UI hang after `.Result` / `.Wait()`, a `Task` that never completes, a finalizer-queue stall, GC stuck in gen 2, LOH fragmentation, ever-growing process memory.
- The user works on a Rhino / Grasshopper plugin (.NET Framework 4.8 or RhinoCore .NET 7) and needs to attach to `Rhino.exe`.
- The user mentions `<Private>true</Private>` / `<Private>false</Private>` on `<Reference>` items, NuGet runtime drift, AssemblyLoadContext, or `app.config` / `bindingRedirect` issues.
- A managed crash dump (`.dmp` / minidump) needs analysis.

## When NOT to use

- Code is F# or VB.NET. The runtime tooling applies, but syntax-level guidance differs.
- Code is not .NET (Java, Go, Node.js, Python, native C++). Pick the matching skill.
- The question is purely about C# language features without a runtime symptom or debugger session.

## Sourcing current docs (Context7 + Microsoft Learn)

The .NET stack is owned end-to-end by Microsoft. Microsoft Learn is the primary source. Do not paraphrase debugger commands, SOS extension flags, or `dotnet-*` CLI options from memory — look them up.

**Context7 MCP, when available, is the first stop.** Resolve with `mcp__context7__resolve-library-id`, then fetch with `mcp__context7__get-library-docs`. Useful library ids:

- `microsoft/dotnet` — .NET runtime, BCL, language guides.
- `microsoft/visualstudio-debugger` — Visual Studio Debugger windows, Tasks, Parallel Stacks, Edit and Continue, hot reload.
- `microsoft/dotnet-diagnostics` — `dotnet-dump`, `dotnet-trace`, `dotnet-counters`, `dotnet-gcdump`, `dotnet-stack`, `dotnet-symbol`.
- `microsoft/windbg` — WinDbg + SOS extension (`!dumpheap`, `!gcroot`, `!finalizequeue`, `!analyze`).
- `microsoft/aspnetcore` — when the symptom involves ASP.NET Core hosting / DI / middleware.
- `dotnet/runtime` and `dotnet/diagnostics` — GitHub source repos, useful for runtime internals when Learn is too high-level.

**Microsoft Learn URLs to prefer over secondary sources:**

- C# / .NET debugger fundamentals: `https://learn.microsoft.com/visualstudio/debugger/`
- Async debugging (Tasks window, parallel watch): `https://learn.microsoft.com/visualstudio/debugger/walkthrough-debugging-a-parallel-application`
- Diagnostics CLI tools: `https://learn.microsoft.com/dotnet/core/diagnostics/`
- `dotnet-dump`: `https://learn.microsoft.com/dotnet/core/diagnostics/dotnet-dump`
- `dotnet-trace`: `https://learn.microsoft.com/dotnet/core/diagnostics/dotnet-trace`
- `dotnet-counters`: `https://learn.microsoft.com/dotnet/core/diagnostics/dotnet-counters`
- `dotnet-gcdump`: `https://learn.microsoft.com/dotnet/core/diagnostics/dotnet-gcdump`
- WinDbg SOS reference: `https://learn.microsoft.com/dotnet/core/diagnostics/sos-debugging-extension`
- SOS commands: `https://learn.microsoft.com/dotnet/core/diagnostics/sos-debugging-extension-windows`
- GC fundamentals (gens, LOH, server vs workstation): `https://learn.microsoft.com/dotnet/standard/garbage-collection/fundamentals`
- Performance counters and EventPipe: `https://learn.microsoft.com/dotnet/core/diagnostics/eventpipe`
- ProcDump: `https://learn.microsoft.com/sysinternals/downloads/procdump`
- Crash and hang dumps: `https://learn.microsoft.com/visualstudio/debugger/using-dump-files`
- Symbols (`.pdb`, symbol servers): `https://learn.microsoft.com/visualstudio/debugger/specify-symbol-dot-pdb-and-source-files-in-the-visual-studio-debugger`
- Assembly binding logs (`fuslogvw` / runtime binding logs on .NET Framework): `https://learn.microsoft.com/dotnet/framework/tools/fuslogvw-exe-assembly-binding-log-viewer`
- AssemblyLoadContext (.NET 6+): `https://learn.microsoft.com/dotnet/core/dependency-loading/loading-managed`
- .NET Framework 4.8 specifics (Rhino / Grasshopper plugin context): `https://learn.microsoft.com/dotnet/framework/`
- C# language reference: `https://learn.microsoft.com/dotnet/csharp/language-reference/`

**Non-Microsoft tools used alongside .NET — official docs:**

- JetBrains Rider debugger: `https://www.jetbrains.com/help/rider/Debugging_Code.html`
- JetBrains dotTrace / dotMemory: `https://www.jetbrains.com/help/profiler/` and `https://www.jetbrains.com/help/dotmemory/`
- BenchmarkDotNet (when "is this a perf bug or a correctness bug" comes up): `https://benchmarkdotnet.org/articles/overview.html`

**Rule when sources disagree:** the live `dotnet-<tool> --help` and SOS `!help` output are final. Microsoft Learn and Context7 are second. Older blog posts (especially pre-.NET 6) often cite retired tooling — treat as historical context, not present truth. If the user is on .NET Framework 4.8 (Rhino plugin work), explicitly check that the Microsoft Learn page applies to net48 and not just modern .NET, since several diagnostics tools (`dotnet-counters`, `dotnet-gcdump`) only attach to .NET Core / .NET 5+ processes.

## Tool ladder

Pick by host environment and what's already installed.

### Live debugging (preferred when reproducible)

1. **Visual Studio (Windows)** — best experience for both .NET Framework 4.8 and modern .NET. Native + managed mixed mode supported. Required for net48 plugin work.
2. **JetBrains Rider** — cross-platform, equivalent feature set to Visual Studio for managed-only code.
3. **VS Code + C# Dev Kit (or `ms-dotnettools.csharp` + `ms-dotnettools.csdevkit`)** — modern .NET only. Limited support for .NET Framework 4.8 (use Visual Studio for net48).
4. **`dotnet` CLI debug** — `dotnet run` then attach by PID with one of the above.

### Crash / hang dump analysis (when not reproducible)

1. **`dotnet-dump`** (cross-platform, modern .NET): capture and analyze.
   ```
   dotnet tool install -g dotnet-dump
   dotnet-dump collect -p <pid>
   dotnet-dump analyze core_<timestamp>
   ```
2. **`dotnet-gcdump`** for managed heap snapshots without a full dump:
   ```
   dotnet tool install -g dotnet-gcdump
   dotnet-gcdump collect -p <pid>
   ```
   Open the `.gcdump` in Visual Studio (File -> Open -> select the `.gcdump`) or PerfView.
3. **WinDbg + SOS** (Windows, required for net48 dumps and the most powerful for any .NET dump).
4. **ProcDump (Sysinternals)** to capture dumps without a debugger:
   ```
   procdump -ma -e <pid>                 First-chance unhandled exception, full dump.
   procdump -ma -t <pid>                 Capture on process termination.
   procdump -ma -h <pid>                 Capture on hang (window stops responding).
   procdump -ma -c 90 -s 5 <pid>         Capture if CPU > 90 percent for 5 seconds.
   ```

### Profilers / counters (when "slow" or "leaks" without exception)

1. **`dotnet-counters`** — live gen 0/1/2 sizes, allocation rate, exception count, threadpool queue depth.
   ```
   dotnet-counters monitor -p <pid> --counters System.Runtime,Microsoft.AspNetCore.Hosting
   ```
2. **`dotnet-trace`** — captures EventPipe traces (.nettrace) for SpeedScope, PerfView, Visual Studio.
   ```
   dotnet-trace collect -p <pid> --providers Microsoft-DotNETCore-SampleProfiler
   ```
3. **JetBrains dotTrace / dotMemory** — GUI profiling and heap diffing.
4. **PerfView (Windows)** — ETW-based, free, deep but unforgiving UI. Best for net48 GC investigation.

### Net48 specifics

- .NET Framework 4.8 runs only on Windows. There is no `dotnet-dump` for net48 dumps; use **WinDbg + SOS** for post-mortem.
- For live debugging: Visual Studio. Set "Just My Code" off when stepping through framework or third-party code.
- For Rhino / Grasshopper plugins, attach to `Rhino.exe`. See the dedicated section below.

## Workflow

### 1. Decide live vs dump

- Reproducible on demand -> live debug. Cheaper iteration.
- Intermittent / production -> capture a dump (procdump on terminate or on first-chance), analyze offline.

### 2. Set the right exception break

In Visual Studio: Debug -> Windows -> Exception Settings (Ctrl+Alt+E).

- **User-unhandled** (default): break only when an exception leaves user code. Misses exceptions caught by frameworks.
- **Thrown** (first-chance): break the moment the exception is constructed, before any `catch`. Use this when you suspect an exception is being swallowed.
- Tick `Common Language Runtime Exceptions` to break on all CLR exceptions, then narrow to a specific type (e.g. `System.InvalidOperationException`).
- For "exception is somewhere in this assembly", add a Filter in the Exception Settings entry (gear icon).

In WinDbg + SOS:

```
sxe clr           Stop on managed first-chance exception.
sxe -c "!pe;g" clr   On managed exception, print it then continue (cheap monitoring).
```

### 3. Use the right breakpoint type

- **Line / function breakpoint** — basic.
- **Conditional breakpoint** — right-click the red dot -> Conditions -> `i == 100 && customer.Id == "X"`.
- **Hit count** — Conditions -> Hit Count -> "is a multiple of 1000".
- **Tracepoint** ("When Hit" -> "Log a message", uncheck "Continue execution"=false to keep running) — emit a string to the Output window without pausing. Best for racy or async flow.
- **Function breakpoint without a file** — Debug -> New Breakpoint -> Function (`Namespace.Class.Method`). Useful when the assembly is decompiled or there's no source.
- **Data breakpoint (.NET 6+ only)** — break when a specific object's field changes. Right-click in the Locals or Watch window -> Break When Value Changes. Not available on .NET Framework 4.8.

### 4. Drive the debugger

#### Visual Studio key windows

- **Call Stack** (Ctrl+Alt+C). Right-click -> Show External Code if frames are missing. Toggle "Just My Code" off when needed.
- **Locals** (Ctrl+Alt+V, L) and **Autos**.
- **Watch** (Ctrl+Alt+W, 1..4). Supports format specifiers: `obj,nq` (no quotes), `i,h` (hex), `arr,5` (first 5).
- **Immediate Window** (Ctrl+Alt+I). Run any C# expression in the current frame, including method calls. Side-effect-free expressions only when "Just My Code" is on.
- **Threads** (Ctrl+Alt+H). Right-click a thread -> Switch To Frame.
- **Parallel Stacks** (Ctrl+Shift+D, S). Visualize all threads' call stacks. Essential for deadlock diagnosis.
- **Parallel Watch** (Debug -> Windows -> Parallel Watch -> 1..4). Same expression evaluated on every thread.
- **Tasks Window** (Ctrl+Shift+D, K). All in-flight `Task` and async state machines, status (Running, Awaiting, Completed), location, parent/child relationship. The fastest way to find an `await` that never resumes.
- **Modules** (Ctrl+Alt+U). What's loaded, where from, symbol status. Use it when a `MissingMethodException` smells like a binding-redirect issue.

#### WinDbg + SOS cheatsheet

Load SOS once attached to a managed process or dump:

```
.loadby sos clr            (.NET Framework)
.loadby sos coreclr        (.NET Core / .NET 5+)
.cordll -ve -u -l          If SOS load fails, force CLR debug DLL refresh.
!eeversion                 Confirm SOS matches the CLR version.
```

Common SOS commands:

```
!threads                   All managed threads, GC mode, exception state.
!clrstack                  Managed call stack of current thread.
!clrstack -p               With parameters.
!clrstack -a               With locals.
~*e !clrstack              Managed call stack on every thread.
!pe                        Print the current managed exception.
!dso                       Dump stack objects (managed objects on this thread's stack).

!do <addr>                 Dump object.
!da <addr>                 Dump array.
!dumpheap -stat            Type histogram across the entire managed heap.
!dumpheap -mt <mt>         All instances of a method table.
!dumpheap -type System.String -min 1024  Find big strings.
!gcroot <addr>             Why is this object alive? Walks every reference path.
!finalizequeue             Pending finalizers; if huge, finalizer thread is stuck.
!syncblk                   Active sync blocks (managed locks); shows owners and waiters.
!runaway                   CPU time per thread.
!eeheap -gc                Generation sizes, LOH, segments.
!analyze -v                AutoTriage; tries to identify the bug.
```

For modern .NET, `dotnet-dump analyze` accepts the same SOS commands without needing WinDbg.

## Async / Task / await diagnostics

This is where most modern C# bugs live. Treat `async` like a careful state machine, not a goroutine.

### `.Result` and `.Wait()` deadlocks

The classic pattern:

```csharp
// In a UI thread (WinForms / WPF / Rhino main thread) or any context with
// a SynchronizationContext:
public string GetData()
{
    return GetDataAsync().Result;       // DEADLOCK if GetDataAsync awaits
                                        // back to the captured context.
}
```

Why: `GetDataAsync` captures the current `SynchronizationContext` at every `await`. When it tries to resume, it posts the continuation back to that context, but the context is blocked on `.Result`. Both wait forever.

In the debugger:

1. The UI thread is parked in `WaitForSingleObjectEx` or `Monitor.Wait`.
2. Open the **Tasks** window. The async method is in state `Awaiting` and never moves.
3. Fix one of three ways:
   - Make the caller `async` and `await` the result. This is correct.
   - In library code, use `ConfigureAwait(false)` on every `await` so continuations don't capture the context.
   - As a last resort, marshal off the UI thread: `Task.Run(() => GetDataAsync()).GetAwaiter().GetResult()`. Still a smell.

### ConfigureAwait misuse

Rule of thumb:

- **Library code** (no UI, no per-request context): `await x.ConfigureAwait(false)` on every awaited call. Prevents accidental context capture and improves throughput.
- **Application code** that touches UI / Rhino document / per-request state: keep `await x` (which is `ConfigureAwait(true)`) so you resume on the right thread.
- ASP.NET Core: there is no `SynchronizationContext`, so `ConfigureAwait(false)` is a micro-optimization and rarely required.

To detect: in the Tasks window, if continuations are pinned to a specific `SynchronizationContext` you can see it in the per-task scheduler. Or in WinDbg, `!syncblk` shows the captured context object.

### `await` that never resumes

Open Tasks window. Filter to `Awaiting`. The status column shows what each task is waiting on (a `TaskCompletionSource`, a `Task.WhenAll`, a `SemaphoreSlim.WaitAsync`).

Common causes:

- A `TaskCompletionSource<T>` was created but `SetResult` / `SetException` is never called on the failure path. Always wrap producers in `try`/`catch` and set the exception.
- `SemaphoreSlim.WaitAsync` followed by an exception that skips `Release()`. Use `try`/`finally`.
- `CancellationToken` never observed. Use `cancellationToken.ThrowIfCancellationRequested()` and pass the token through.

### ValueTask continuations

`ValueTask<T>` is single-await. Awaiting twice or calling both `.AsTask()` and `await` is undefined.

In the debugger, if a `ValueTask` shows `_obj == null` and `_result` set, it's the synchronous case (returns immediately). If `_obj` is a `Task` or `IValueTaskSource`, it's the async case. Awaiting more than once on the latter throws `InvalidOperationException`.

Avoid:

```csharp
ValueTask<int> v = GetValueAsync();
int a = await v;        // ok
int b = await v;        // BUG: second await on a ValueTask
```

### Async state machine in the debugger

When stopped inside an `async` method, the **this** pointer in the call stack is the compiler-generated `<MethodName>d__0` struct/class. Inspect:

- `<>1__state` — current state (-1 = running, -2 = completed, -3 = ...).
- `<>t__builder` — `AsyncTaskMethodBuilder`.
- `<>u__1`, `<>u__2`, ... — captured awaiters for each `await`.
- Local variables hoisted from the source method.

In Visual Studio, the **Async Call Stacks** view (Ctrl+Shift+D, S, then choose "Async Call Stacks") joins these state machines into a logical stack so you can read `Caller -> awaited -> awaited -> Current` across thread boundaries.

## GC and memory diagnostics

### Quick triage

`dotnet-counters monitor -p <pid> --counters System.Runtime`

Watch for:

- `gen-2-gc-count` rising fast -> too much promotion, large allocations, or long-lived caches.
- `gc-heap-size` growing without bound -> leak.
- `loh-size` large or growing -> Large Object Heap pressure.
- `time-in-gc` over 20 percent -> the program is allocation-bound.

### Heap snapshot diff

1. `dotnet-gcdump collect -p <pid> -o before.gcdump` at a quiet point.
2. Exercise the suspected leak path.
3. `dotnet-gcdump collect -p <pid> -o after.gcdump`.
4. Open both in Visual Studio (Memory Usage tool) or PerfView; subtract.

In dotMemory: take two snapshots, click "Compare". Filter to "New Objects" and sort by retained size.

### SOS heap walk

```
!eeheap -gc                      Heap layout: gen 0/1/2/LOH/POH segments.
!dumpheap -stat                  Histogram by type, ascending count.
!dumpheap -stat -min 85000       LOH-sized objects only.
!dumpheap -mt <mt> -short        All instances of one type.
!gcroot <addr>                   Why is this object still rooted?
!objsize <addr>                  Retained size of an object graph.
!finalizequeue                   Anything stuck in finalization?
```

### Large Object Heap (LOH)

- Threshold: any allocation >= 85,000 bytes goes to LOH.
- LOH is collected only on gen 2 GC and (historically) not compacted by default.
- Compaction on demand:

```csharp
GCSettings.LargeObjectHeapCompactionMode = GCLargeObjectHeapCompactionMode.CompactOnce;
GC.Collect();
```

  Use sparingly; this is a stop-the-world full compacting GC.
- Common LOH abusers: large `byte[]` for I/O, big `string` concatenations, JSON serialization buffers. Use `ArrayPool<byte>.Shared` and `RecyclableMemoryStream` to recycle buffers.

### Generation reasoning

- Allocate -> gen 0.
- Survives one GC -> gen 1.
- Survives two -> gen 2 (long-lived).
- A leak is "objects of type X have a non-trivial gen 2 count and `!gcroot` shows a static field / event handler / Timer / Task holding them".

### Finalizer / IDisposable leaks

- Symptom: `!finalizequeue` is huge, finalizer thread is busy, gen 2 keeps growing.
- Root cause: types with finalizers being collected from gen 2 instead of disposed promptly.
- Fix: implement `IDisposable` correctly and `using` it. The class should suppress its finalizer in `Dispose`:

```csharp
public void Dispose()
{
    Dispose(true);
    GC.SuppressFinalize(this);
}
```

- Find leaked disposables: `!dumpheap -type <YourClass>` and `!gcroot <addr>` for each instance.

### Event-handler leaks

A long-lived publisher holding a delegate to a short-lived subscriber keeps the subscriber alive forever.

- Symptom: subscribers expected to be GCed are still in `!dumpheap -stat`. `!gcroot` traces them through `EventHandler -> _target`.
- Fix: unsubscribe in `Dispose`, or use `WeakEventManager` (WPF) / weak reference patterns.

## Assembly loading and binding diagnostics

### `FileNotFoundException: Could not load file or assembly 'X'`

In Visual Studio, **Modules** window shows what loaded. The Output window with "Show output from: Debug" prints binding errors.

Enable Fusion Log (.NET Framework 4.8):

```
HKLM\Software\Microsoft\Fusion
  EnableLog       = 1   (DWORD)
  ForceLog        = 1   (DWORD)
  LogPath         = "<repo-path>"   (REG_SZ, ensure dir exists)
```

Reproduce, inspect logs in the configured folder, then reset `EnableLog` to 0 (Fusion logging adds overhead).

For modern .NET, set:

```
COREHOST_TRACE=1
COREHOST_TRACEFILE=<repo-path>
```

### `BadImageFormatException`

Almost always an x86 vs x64 mismatch.

- 32-bit process trying to load a 64-bit assembly, or vice versa.
- Check the project: `<PlatformTarget>x64</PlatformTarget>` (or `AnyCPU` with `Prefer32Bit=false`).
- Confirm with `corflags MyAssembly.dll` (Windows SDK).

### `MissingMethodException` after a NuGet upgrade

A binding redirect didn't refresh, or a type's API changed.

1. Check the `.config` (net48) for `<bindingRedirect oldVersion="0.0.0.0-X" newVersion="Y" />` mapping the resolved version to what's actually on disk.
2. For modern .NET, `<PackageReference>` resolves transitively; check `dotnet list package --include-transitive`.
3. Inspect the actual loaded version: Modules window in VS, or `[assembly: AssemblyVersion]` via `AssemblyName.GetAssemblyName(path)`.

### AssemblyLoadContext (modern .NET)

If a plugin host loads its own `AssemblyLoadContext`:

- `AssemblyLoadContext.GetLoadContext(typeof(T).Assembly)` shows which context owns a type.
- Type identity is per-context: two contexts can each load `MyType`, and `t1 is MyType` returns false across them.
- Memory leaks if a non-collectible context pins an assembly forever.

## Net48 + Rhino / Grasshopper plugin debugging

This section captures patterns specific to Rhino plugin work (.NET Framework 4.8 host).

### Attaching to Rhino

1. Build the plugin in Debug. Confirm the `.pdb` is next to the `.gha` / `.rhp` in Rhino's plugin output directory.
2. Start Rhino and load the plugin (open a `.gh` file that uses your component).
3. In Visual Studio: Debug -> Attach to Process -> select `Rhino.exe`. For "Attach to" choose "Managed (.NET Framework 4.x) code". Add "Native code" as well if your plugin P/Invokes a C++ DLL.
4. Open the plugin source. Set breakpoints. They will appear hollow until the assembly is loaded; once Rhino loads the plugin, they fill in.

### Rhino main thread

Rhino's UI thread is the main thread of `Rhino.exe`. It owns:

- The Rhino document (`RhinoDoc`).
- The Grasshopper canvas (`GH_Document`, `GH_Canvas`).
- All UI work.

Almost every `RhinoCommon` and `Grasshopper` API call must happen on this thread. Touching the document from a worker thread results in undefined behavior, intermittent crashes, or `InvalidOperationException` from a UI control.

To marshal back:

```csharp
Rhino.RhinoApp.InvokeOnUiThread((Action)(() =>
{
    // RhinoCommon calls here.
}));
```

In the Threads window, the main thread is the one with frames including `Eto.Forms`, `RhinoApp`, `MFC`, or `WindowsFormsApplicationBase.Run`.

### `GH_TaskCapableComponent<T>` async path

Grasshopper async components have a specific lifecycle:

- `BeforeSolveInstance` runs on UI thread -> kicks off worker tasks.
- `SolveInstance` is called once per task with `RunCount`. The first call (`InPreSolve`) registers the task; subsequent calls retrieve results.
- `AfterSolveInstance` runs on UI thread -> applies results.

Common bugs to break on:

- Calling `RhinoDoc.ActiveDoc` or any `GH_Param.AddVolatileData` from the worker `Task` body. Move that code into `AfterSolveInstance` or the post-solve closure.
- Capturing component-local state that changes between solves. Snapshot it inside `BeforeSolveInstance`.
- Blocking on `Task.Result` inside `SolveInstance` defeats the point and can deadlock.

To debug:

1. Set a breakpoint on the lambda body of the `Task.Run(() => { ... })` worker.
2. When hit, open the Threads window and confirm you are NOT on the main thread.
3. Step out into `AfterSolveInstance`; confirm you ARE on the main thread (look for the Eto / WinForms message-loop frames).

### `<Private>true</Private>` vs `<Private>false</Private>`

In a `.csproj` `<Reference>` item:

- `<Private>true</Private>` (default for project references): the referenced DLL is **copied to the output directory** during build.
- `<Private>false</Private>`: the DLL is **not copied**. The plugin assumes the host (Rhino) provides it at runtime.

For Rhino plugins, RhinoCommon / Grasshopper / Eto are provided by Rhino. Keep these at `<Private>false</Private>` to avoid shipping duplicate copies that load from the wrong path and produce two different `Type` identities (the dreaded "type X cannot be cast to type X" error).

For your own NuGet dependencies that Rhino does not provide, keep `<Private>true</Private>` so they ship next to your `.gha` / `.rhp`.

If the plugin fails to load with `FileNotFoundException` on a Rhino-provided assembly: a private copy in the plugin folder differs from Rhino's. Delete the private copy.

If the plugin loads but throws `MissingMethodException` at runtime: a private copy is **older** than Rhino's. Either update the private copy or set `<Private>false</Private>`.

### Net48 build constraints (project-specific)

When debugging or patching plugin source:

- Avoid `string.Contains(value, StringComparison)` — net48 only has `Contains(string)`. Use `IndexOf(value, StringComparison.OrdinalIgnoreCase) >= 0`.
- Avoid `HashCode.Combine` — not in net48. Roll a manual hash:
  ```csharp
  unchecked
  {
      int hash = 17;
      hash = hash * 31 + (a?.GetHashCode() ?? 0);
      hash = hash * 31 + (b?.GetHashCode() ?? 0);
      return hash;
  }
  ```
- Avoid file-scoped `#nullable enable` project-wide; use `#nullable disable` per file when nullability annotations leak in.
- Test csproj must explicitly `<Reference Include="RhinoCommon">` with `<HintPath>` to the Rhino install. Project references alone are not enough.

## Common bug patterns

### `NullReferenceException` deep in a chain

1. In Exception Settings, enable Thrown break for `System.NullReferenceException`. Reproduce.
2. The break point is the line that dereferenced null. Hover the chain expressions (`a.b.c.d`) — VS shows which segment is null.
3. Fix at the source of the null, not at the throw site. A null check at the throw site usually masks a different bug.

### `InvalidOperationException: Collection was modified`

- Cause: a `foreach` over a collection while the same thread or another thread modifies it.
- Single-threaded fix: collect changes into a temp list, apply after the loop.
- Multi-threaded fix: use `ConcurrentDictionary` / `ConcurrentBag` / `ImmutableList` or a lock around iterate-and-modify.

### `OutOfMemoryException` in 32-bit process

- 32-bit .NET processes get ~2 GB of address space, less if fragmented.
- For net48 plugins inside Rhino: Rhino is 64-bit, so the plugin is too. OOM here is real, not address-space exhaustion.
- Diagnose with a heap dump; almost always a leak (events, statics, caches without bounds, MemoryStream not disposed).

### `TypeLoadException` on plugin load

- Confirm target framework matches host: net48 plugin into Rhino 7, net7.0 plugin into Rhino 8.
- A type has a missing dependency. Open in `dotPeek` / ILSpy and check its assembly references against what's in the plugin folder + Rhino folder.

### P/Invoke crash from managed side

- The CLR shows `AccessViolationException` originating from your `[DllImport]` call.
- Switch to mixed-mode debugging in Visual Studio (project properties -> Debug -> Enable native code debugging).
- The crash now stops in the C++ side. Continue with the **cpp-debugger** skill from there.

### Threadpool starvation / "everything is slow"

- `dotnet-counters` shows `threadpool-queue-length` rising and `threadpool-thread-count` saturated.
- Root cause is almost always blocking calls (`.Result`, `.Wait()`, `Task.Run` wrapping blocking IO) running on threadpool threads, starving everything else.
- Fix: convert blocking IO to true async (`HttpClient.GetAsync`, `SqlConnection.OpenAsync`, file IO with `FileStream(useAsync: true)`).

## Quick decision tree

```
Got a managed exception?
  Reproducible?            -> Visual Studio, Exception Settings -> Thrown for that type, run.
  Not reproducible?        -> procdump -ma -e <pid>, analyze with dotnet-dump or WinDbg+SOS.

Hang / deadlock?
  Live           -> attach VS, Parallel Stacks, look for cycles in lock ownership.
  Production     -> procdump -ma -h <pid> on the hung process, !syncblk + !threads in WinDbg.

Memory growth?
  dotnet-counters monitor first.
  Two dotnet-gcdump snapshots, diff.
  !dumpheap -stat for the top types, !gcroot for the leakers.

UI freeze right after an async call?
  Tasks window. Look for Awaiting state machines parked on a captured SynchronizationContext.
  Suspect .Result / .Wait() / Task.Run().GetAwaiter().GetResult() on the UI thread.

Plugin won't load (Rhino, ASP.NET, anything)?
  Modules window or Fusion log. Mismatched version, missing transitive dep, or x86/x64.

Slow code, no exception?
  dotnet-trace, then SpeedScope. Or dotTrace if available.
```

## Logging while you debug

Sometimes pausing changes the bug (Heisenbugs, races). Use Tracepoints instead of breakpoints:

1. Right-click in the gutter -> Insert Tracepoint.
2. Set "When Hit" message: `Entered {this.GetType().Name}.{methodName}, x={x}`.
3. Uncheck "Continue execution" to keep running.
4. Output appears in the Output window, "Show output from: Debug".

For production, prefer a logger (`ILogger`, NLog, Serilog) with a structured-event sink. Don't ship `Console.WriteLine`.

## Verification flags

Where flags or commands below are non-obvious or version-sensitive, confirm with the indicated `--help`:

- `procdump` switches: `verify: procdump.exe /?`. Behavior differs between v9 and v11.
- `dotnet-dump` and `dotnet-trace` subcommands and providers: `verify: dotnet-dump --help`, `dotnet-trace --help`, `dotnet-trace list-profiles`.
- `corflags` (Windows SDK location varies by SDK version): `verify: where corflags`, then `corflags /?`.
- `ttd.exe` (WinDbg Time Travel Debugging) flags: `verify: ttd.exe /?`.
- WinDbg / cdb extension command syntax differs slightly across CLR versions: `verify: !help` after loading SOS, and `!sos.help` for full list.
