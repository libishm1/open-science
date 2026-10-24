---
name: rhinocommon-debugger
description: This skill should be used when the user is debugging a Rhino or Grasshopper plugin (`.rhp` / `.gha`) built against McNeel's RhinoCommon .NET API on Rhino 7 or Rhino 8, attaches a managed debugger to `Rhino.exe`, or hits RhinoCommon-specific failures like `Rhino.Runtime.RhinoException`, `Rhino.UnitConversionException`, `Mesh.IsValid` false, `Brep.IsValidWithLog` reporting edge / trim / seam errors, broken `Curve` topology, `RhinoMath.UnsetValue` propagation, `Transform.ZeroTransformation` or non-invertible matrices, `BadImageFormatException` from x86/x64 mismatch with Rhino, `FileNotFoundException` for `RhinoCommon.dll` / `Grasshopper.dll` / `GH_IO.dll`, `MissingMethodException` after a Rhino version bump, `TypeLoadException` from a plugin built against the wrong RhinoCommon, `DllNotFoundException` for `rhcommon_c.dll` / `rhcommon_opennurbs.dll`, components missing on the canvas, components throwing in `SolveInstance`, GH document hanging at `Run=true`, threading bugs in `GH_TaskCapableComponent<T>`, `RhinoApp.InvokeOnUiThread` misuse, plugin load failures (`PluginLoadTime.Disabled` / `Errored`), or bad `OnLoad` results. For general .NET debugging without RhinoCommon symptoms, defer to the `csharp-debugger` skill. For native C++ Rhino SDK / openNURBS plugins, defer to the `cpp-debugger` skill.
---

# RhinoCommon Debugger

Procedural guide for debugging Rhino plugins (`.rhp`) and Grasshopper assemblies (`.gha`) built against McNeel's RhinoCommon .NET API. Targets the reference plugin StonePack project's reality: .NET Framework 4.8 today, Rhino 7 + Rhino 8 installed, Visual Studio on Windows. This skill covers only what is specific to RhinoCommon. For general .NET / C# debugger workflow, exception triage, GC, async, assembly binding, and `<Private>` semantics, defer to the `csharp-debugger` skill.

## When to use

Use this skill when the symptoms touch RhinoCommon, Grasshopper, or the Rhino host process:

- The code references `Rhino.Geometry.*`, `Rhino.DocObjects.*`, `Rhino.Display.*`, `Rhino.Render.*`, `Rhino.UI.*`, `Rhino.Commands.*`, `Rhino.RhinoApp`, or `Rhino.RhinoDoc`.
- The code uses Grasshopper.Kernel: `GH_Component`, `GH_TaskCapableComponent<T>`, `GH_Document`, `IGH_DataAccess`, `GH_Structure<T>`, `GH_AssemblyInfo`.
- The exception is RhinoCommon-typed: `Rhino.Runtime.RhinoException`, `Rhino.UnitConversionException`, geometry-validity exceptions, or any failure path documented in `Brep.IsValidWithLog`, `Mesh.IsValid`, `Curve.IsValid`.
- The user is attaching a managed debugger to `Rhino.exe` to step into a `.gha` or `.rhp`.
- Symptoms include: Rhino crash on plugin load, `BadImageFormatException` against Rhino's bitness, `FileNotFoundException` for `RhinoCommon.dll` / `Grasshopper.dll` / `GH_IO.dll`, `MissingMethodException` after a Rhino version bump, `TypeLoadException` from a plugin built against the wrong RhinoCommon, `DllNotFoundException` for `rhcommon_c.dll` / `rhcommon_opennurbs.dll`, plugin loads but components do not appear on the canvas, components appear but throw in `SolveInstance`, the GH document hangs after `Run=true`.
- Geometry errors: `Mesh.IsValid` false (naked / non-manifold / degenerate edges, NaN vertex normals); `Brep.IsValid` false with detailed `IsValidWithLog` strings (edge tolerance, trim out of domain, seam not on a knot); `Curve` not closed when expected, not planar (`TryGetPlane` returns false), parameter domain reversed, irregular knot vector.
- Transform errors: composing in the wrong order (RhinoCommon multiplies right to left), or applying a non-orthogonal `Transform` to a `Plane` and breaking it.
- Unit / tolerance gotchas: `RhinoDoc.ModelAbsoluteTolerance` vs an ad-hoc tolerance, document units changing under your feet, mm vs meter mismatch in physics-based code.
- Threading: any RhinoCommon mutator called off the UI thread, misuse of `RhinoApp.InvokeOnUiThread`, `GH_TaskCapableComponent` `SolveInstance` racing background work, `RhinoDoc` accessed from a worker.
- Native interop relevant to reference plugin StonePack: `rhcommon_c.dll` missing in a stripped test environment, `Mesh.Append` corrupting topology when called off-thread, geometric tolerance drift after `Transform.ChangeBasis`.
- Plugin load order: `PluginLoadTime.Disabled` / `Errored`, the plugin's `OnLoad` hook returning a bad result, plugin GUID collision, missing or malformed `GH_AssemblyInfo`.

## When NOT to use

- The bug is in a non-Rhino .NET project (general C#, ASP.NET, EF, console app). Use the `csharp-debugger` skill.
- The bug is in a native C++ Rhino SDK plugin (`.cpp`, openNURBS, `CRhinoCommand`). Use the `cpp-debugger` skill.
- The user is asking about Grasshopper Python (GhPython, IronPython 2.7, or the new CPython 3 component) without a managed debugger session. That is a different workflow and is not covered here.
- The user wants help authoring RhinoCommon code without a runtime symptom. This skill is procedural debugging only.

## Sourcing current docs (Context7 + official primary sources)

McNeel owns the surface. Do not paraphrase RhinoCommon API method names, parameter orders, exception types, or Grasshopper SDK lifecycle hooks from memory. Look them up.

**Context7 MCP, when available, is the first stop** for any RhinoCommon type, Grasshopper SDK class, or Rhino.Inside topic. Resolve a library id with `mcp__context7__resolve-library-id`, then fetch with `mcp__context7__get-library-docs`. RhinoCommon itself is closed source, so Context7 will most often return developer-samples and Rhino.Inside repos. Library ids worth trying first:

- `mcneel/rhino-developer-samples` — McNeel's official sample plugin tree, organized by Rhino version. The closest thing to canonical example code for components, commands, display conduits, and `GH_TaskCapableComponent`.
- `mcneel/rhinocommon` — historical RhinoCommon repo (now mostly redirects, still useful).
- `mcneel/Grasshopper` — Grasshopper SDK examples and issues.
- `mcneel/Rhino.Inside` — running Rhino inside other host processes; relevant when the bug involves `AssemblyLoadContext` or Rhino.Inside.Cli.
- `mcneel/Rhino.Inside.Revit` — production-grade Rhino-Inside-host integration. A goldmine for plugin-load and AssemblyLoadContext patterns.
- `microsoft/dotnet` — cross-cutting .NET runtime and tooling docs.

**McNeel official primary sources** (prefer these over blog posts and Stack Overflow when Context7 is offline):

- RhinoCommon API reference: `https://developer.rhino3d.com/api/rhinocommon/`
- Rhino developer guides (versioned per Rhino release): `https://developer.rhino3d.com/guides/`
- Grasshopper SDK guides: `https://developer.rhino3d.com/guides/grasshopper/`
- Rhino.Inside docs: `https://developer.rhino3d.com/guides/rhino.inside/`
- Discourse (community plus official answers): `https://discourse.mcneel.com/`
- Rhino developer category (Serengeti): `https://discourse.mcneel.com/c/serengeti/8`

**Open-source RhinoCommon-using repos that act as reference for idiomatic usage and known pitfalls.** RhinoCommon itself is closed source, so use these for patterns:

- `https://github.com/mcneel/rhino-developer-samples` — official sample tree.
- `https://github.com/mcneel/Rhino.Inside` — host-process integration patterns.
- `https://github.com/mcneel/Rhino.Inside.Revit` — full-scale plugin host with battle-tested load logic.
- `https://github.com/mcneel/compute.rhino3d` — server-side RhinoCommon usage; useful when the bug is "Rhino is running headless".
- GitHub topics for community plugins: `https://github.com/topics/rhinocommon` and `https://github.com/topics/grasshopper`.

**Rule when sources disagree:** McNeel official docs and the developer-samples repo are final. Discourse threads are second tier (the McNeel devs answer there directly, often with definitive code). Random blog posts and old NuGet examples are third tier — treat as hints, not as authority. When in doubt, run the call in a minimal sample, compare, and trust the live behavior.

## Tool ladder

Pick by what is installed and what the symptom looks like. For .NET Framework 4.8 plugin work (the reference plugin StonePack default), Visual Studio on Windows is the only first-class debugger.

1. **Visual Studio (Windows)** — preferred for net48 `.gha` / `.rhp` debugging. Mixed managed-plus-native attach to `Rhino.exe` works out of the box. Required when the plugin P/Invokes a C++ DLL.
2. **JetBrains Rider** — fine for managed-only attach. Same Attach-to-Process workflow. Good when Visual Studio is not installed.
3. **Rhino's own developer console** — for printf-style debugging without a debugger attached:
   - `RhinoApp.WriteLine("...")` writes to the Rhino command line. Cheap and always works.
   - The `_TestStartDebugger` Rhino command opens a debugger-attach prompt. Useful when launching Rhino from outside a debugger and you want to attach mid-session. Verify the command name with Rhino's `_TestList` command on your installed version.
   - The internal `RhinoDebugger` plugin (shipped with Rhino developer builds) exposes lower-level diagnostic commands. Verify availability per Rhino version.
4. **Attach by process name to `Rhino.exe`** — the standard live workflow. In Visual Studio: Debug -> Attach to Process -> filter `Rhino.exe`. Choose code type "Managed (.NET Framework 4.x) code" for net48 plugins; add "Native code" if your plugin P/Invokes.
5. **Breakpoints in `GH_Component.SolveInstance`** — the canonical entry point for component bugs. For multi-branch input, use a conditional breakpoint filtered by `da.Iteration` (the `IGH_DataAccess.Iteration` index of the current solve). Example condition: `da.Iteration == 7`.
6. **`RhinoApp.WriteLine` traces** — when stepping breaks the bug (timing, races, idle UI flushes), use `RhinoApp.WriteLine` instead. Write a one-line stamp at every entry/exit you care about.
7. **Hot reload limitations** — .NET Framework 4.8 plugins do **not** support Edit and Continue or Hot Reload across the Rhino process boundary. Code changes require a Rhino restart (`File -> Exit`, rebuild, relaunch). Rhino 8 in .NET 7 mode supports Hot Reload for some scenarios; verify per Rhino release notes before relying on it.

## Workflow

### 1. Reproduce minimally

Before attaching, get a deterministic repro inside a single `.gh` document.

- Start a fresh, empty Grasshopper document.
- Drop only your component plus the smallest set of inputs that triggers the bug.
- Save the `.gh` to disk so the repro survives Rhino restarts.
- If the bug only fires on a specific `.3dm` model, save a stripped-down model that contains only the failing geometry.

### 2. Build Debug and copy to the plugin folder

For net48 plugins, the build output is a `.gha` (Grasshopper) or `.rhp` (Rhino) plus a `.pdb`. Both must end up in a folder Rhino loads from:

- `%APPDATA%\Grasshopper\Libraries\` for `.gha`.
- `%APPDATA%\McNeel\Rhinoceros\<version>\Plug-ins\<YourPlugin>\` for `.rhp`, or load via Rhino's `_PluginManager` once.
- The matching `.pdb` next to the assembly is required for breakpoints to bind.

The reference plugin StonePack file-copy-only workflow already does this; do not launch Rhino from the build step.

### 3. Attach to `Rhino.exe`

1. Start Rhino. Open the repro `.gh`.
2. In Visual Studio: Debug -> Attach to Process -> filter `Rhino.exe` -> Attach. Confirm the code type is at least "Managed (.NET Framework 4.x) code".
3. Open the plugin source. Set breakpoints. They will appear hollow until Rhino loads the assembly; once it does, they fill in.
4. If breakpoints stay hollow after the component appears on the canvas: the loaded `.gha` is not the one you just built, or its `.pdb` is missing. Check Visual Studio's Modules window for the actual loaded path.

### 4. Capture `RhinoApp.WriteLine` traces

Use `Rhino.RhinoApp.WriteLine(string)` for printf-style instrumentation. The output appears in the Rhino command line and the command history (`F2` to view).

```csharp
Rhino.RhinoApp.WriteLine($"[reference plugin] SolveInstance start, iter={da.Iteration}");
```

Avoid `Console.WriteLine` from inside Rhino — the standard streams are not connected to anything visible by default.

### 5. Capture a managed minidump (when not reproducible live)

Use ProcDump (Sysinternals) to capture a full dump on first-chance unhandled exception or hang:

```
procdump -ma -e Rhino.exe              # Full dump on unhandled exception.
procdump -ma -h Rhino.exe              # Full dump on hang (window stops responding).
procdump -ma -t Rhino.exe              # Full dump on process termination.
```

Verify the exact switches with `procdump.exe /?` — behavior differs between v9 and v11.

For Rhino 7 and Rhino 8 in .NET Framework 4.8 mode: analyze the resulting `.dmp` with **WinDbg + SOS** (`.loadby sos clr`). `dotnet-dump analyze` does not work on net48 dumps.

For Rhino 8 running in .NET 7 / "Rhino on .NET Core" mode: `dotnet-dump analyze <dumpfile>` works. Verify your Rhino install is running on .NET Core by checking `Rhino.Runtime.HostUtils.RunningOnNetCore` (verify property name against the RhinoCommon API ref).

For SOS commands and managed-heap walking, defer to the **csharp-debugger** skill.

## Common bug patterns

### Plugin not loaded

Symptoms: the component does not appear, no error in Rhino's command line, or `_PluginManager` shows the plugin in `Disabled` / `Errored` state.

Steps:

1. Run the `_PluginManager` Rhino command. Find the plugin row. Expand it. The "Load Time" and "Last Error" columns show why Rhino refused to load it.
2. The plugin file may be **locked** by a previous Rhino instance. Close all Rhino instances before rebuilding.
3. The plugin may be missing a hard dependency. Check the plugin folder for any third-party DLL the plugin references with `<Private>true</Private>`. Anything Rhino itself provides (RhinoCommon, Grasshopper, GH_IO, Eto) must be `<Private>false</Private>` — see the `csharp-debugger` skill for the full `<Private>` discussion.
4. If the plugin's `OnLoad(ref string errorMessage)` returns `LoadReturnCode.ErrorShowDialog` or `ErrorNoDialog`, the `errorMessage` string surfaces in `_PluginManager`. Add a `RhinoApp.WriteLine` at the top of `OnLoad` to confirm it is even called.

### Plugin loads, components missing from canvas

Symptoms: `_PluginManager` shows the plugin loaded, but no component appears in any Grasshopper category.

Steps:

1. Confirm the `GH_AssemblyInfo` subclass exists, has a public parameterless constructor, and is the only one in the assembly.
2. Confirm each component's `ComponentGuid` is unique. A duplicate GUID with another loaded plugin silently drops the second registration.
3. Confirm `Exposure` is set (default is `primary`). Exposure `hidden` removes the component from the panel.
4. Check the `Category` and `SubCategory` strings for typos. Grasshopper creates a new tab on demand, so a typo just hides your component under a misspelled tab.
5. Open Grasshopper's `File -> Special Folders -> Components Folder`, confirm the `.gha` is there and timestamped.

### Component throws on first solve

Symptoms: the component appears, turns red on first run, hovering shows an exception.

Steps:

1. Look at the runtime warnings/errors via right-click -> Runtime warnings / errors. The first message is usually the cause.
2. Common offenders inside `SolveInstance`:
   - Null `Curve` / `Brep` / `Mesh` from `da.GetData(...)` because the input was unwired. Always test the result of `GetData` and bail with `AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, ...)` rather than throwing.
   - `Mesh.IsValid` is false. Call `mesh.Check(...)` and inspect the returned `MeshCheckParameters` to see exactly which invariant fails (verify method signature in the RhinoCommon API ref; older versions exposed `IsValidWithLog`).
   - `Brep.IsSolid` is false when downstream code assumes a closed solid. Use `IsValidWithLog(out string log)` and surface the log.
   - Document units mismatch. The component reads `RhinoDoc.ActiveDoc.ModelUnitSystem` (or constructs geometry assuming millimeters) while the user's document is in meters. Convert with `RhinoMath.UnitScale(fromUnits, toUnits)` (verify name and signature).

### Output transforms wrong: "curves fly off into space"

Symptoms: after applying a compound transform (rotate then translate, etc.), curves end up far from the expected location.

Cause: **RhinoCommon's `Transform * Transform` multiplies right to left.** Building `Transform combined = T1 * T2;` and then applying it means `T2` is applied first, then `T1`. This is the OpenGL-style column-vector convention.

Worked example from the reference plugin StonePack project: `Pack2DIrregularSheetV506Component.cs` documents this exact trap. The Rhino 5.0.6 fix in that file flips the multiplication order so curves no longer "fly off in the distance".

Steps:

1. Decide the order in plain English ("first translate to origin, then rotate, then translate to target").
2. Build the compound from right to left: `Transform combined = T_translateToTarget * T_rotate * T_translateToOrigin;`.
3. Apply with `geometry.Transform(combined)`. Each piece of geometry mutates in place (or returns a new instance for value-typed geometry).
4. If the result is still wrong, log the input bounding-box centroid before and after each individual transform. The first `Transform` that moves the centroid to a wildly wrong place is the bug.

Verify: the multiplication-order convention is documented in the RhinoCommon `Transform` API ref. Confirm before relying on this in production code.

### Mesh corruption after multi-thread `Mesh.Append`

Symptoms: `Mesh` produced from a parallel pipeline is invalid, has wrong vertex counts, or crashes on `Bake`.

Cause: **RhinoCommon mutator methods (`Mesh.Append`, `Mesh.Vertices.Add`, `Brep.Append`, etc.) are not thread-safe.** Calling them from multiple threads on the same instance corrupts internal C++ state in `rhcommon_c.dll`.

Steps:

1. Build per-thread results in isolation. Each `Task.Run` body produces its own local `Mesh`.
2. Marshal the merge step to the UI thread, or to a single dedicated worker that owns the destination instance:

```csharp
// In each parallel task:
Mesh local = BuildLocalMesh(input);
return local;

// After Task.WhenAll, on the UI thread:
Mesh combined = new Mesh();
foreach (var local in results)
{
    combined.Append(local);
}
```

3. Verify post-merge with `combined.IsValid` and `combined.Check(...)`. Surface any `MeshCheck` failures via `AddRuntimeMessage`.

### `RhinoMath.UnsetValue` propagating silently

Symptoms: a downstream calculation produces astronomical numbers like `-1.23432101234321e+308`, NaN, or "infinity" geometry.

Cause: `RhinoMath.UnsetValue` is the sentinel `double` for "no value", literally `-1.23432101234321e+308`. RhinoCommon returns it from many APIs when the result is undefined (e.g. `Curve.ClosestPoint` failure, parameter outside domain, intersection miss). Arithmetic on `UnsetValue` produces nonsense without any exception.

Steps:

1. Wherever a RhinoCommon API can return a `double`, check `RhinoMath.IsValidNumber(value)` before using it.
2. For methods that return `bool` plus an `out double`, always check the bool first. The `out` value is undefined on failure.
3. In a pipeline that already produced bad output, set a conditional breakpoint on the suspect variable: `Math.Abs(t) > 1e+300` will catch `UnsetValue` early.

Verify the literal value and the `IsValidNumber` helper signature in the RhinoCommon API ref under `Rhino.RhinoMath`.

### `Transform.ChangeBasis` returning identity unexpectedly

Symptoms: `Transform.ChangeBasis(planeFrom, planeTo)` returns the identity transform when the two planes are clearly different.

Cause: the call signature is non-obvious. `ChangeBasis` requires both source and target frames to be valid orthogonal frames; coplanar or degenerate frames produce a fallback. There are also overloads that take three world axes versus two `Plane` arguments, and they have different semantics.

Steps:

1. Confirm both `Plane` arguments are valid: `plane.IsValid` true, axes orthonormal. A `Plane` constructed from collinear points is invalid.
2. If you really need axis-by-axis control, use the overload `Transform.ChangeBasis(Vector3d xFrom, Vector3d yFrom, Vector3d zFrom, Vector3d xTo, Vector3d yTo, Vector3d zTo)`. Verify the parameter order in the RhinoCommon API ref before relying on it.
3. To debug: print the four basis vectors of each plane (`plane.XAxis`, `plane.YAxis`, `plane.ZAxis`, `plane.Origin`) into `RhinoApp.WriteLine` and confirm they are what you expect.

### `BadImageFormatException` on plugin load

Symptoms: Rhino crashes at startup, or `_PluginManager` shows the plugin as `Errored` with `BadImageFormatException`.

Cause: x86 vs x64 mismatch. Rhino 7 and Rhino 8 are **x64 only**; there is no 32-bit Rhino. A plugin built with `<PlatformTarget>x86</PlatformTarget>` cannot load.

Steps:

1. In the plugin `.csproj`, set `<PlatformTarget>x64</PlatformTarget>` or `<PlatformTarget>AnyCPU</PlatformTarget>` with `<Prefer32Bit>false</Prefer32Bit>`.
2. Confirm with `corflags MyPlugin.gha` (Windows SDK). The `32BIT` flag must be 0 and `PE` must be `PE32+`.
3. Rebuild and copy. Restart Rhino.

For `<Private>` semantics around accidentally shipping a 32-bit transitive dependency, defer to the `csharp-debugger` skill.

### `MissingMethodException` after a Rhino version bump

Symptoms: plugin loaded fine on Rhino 7, breaks on Rhino 8 (or vice versa) at the first call into RhinoCommon with `MissingMethodException`.

Cause: RhinoCommon's ABI changed between major versions. Methods are added, parameters change, and occasionally types move between namespaces.

Steps:

1. Identify the missing method from the exception message (`Method not found: ...`).
2. Open the RhinoCommon API ref and switch the version selector to the running Rhino version. Confirm the signature.
3. Pin the plugin to the lowest API version you actually need. Either:
   - Reference RhinoCommon from the **lowest** Rhino install you support (e.g. Rhino 7's `RhinoCommon.dll` on disk), so the binary stays binary-compatible upward.
   - Or build separate Rhino 7 and Rhino 8 plugin assemblies and ship both.
4. The reference plugin StonePack project default is to reference RhinoCommon via `<HintPath>` to the local Rhino install. Confirm the `.csproj` `<HintPath>` points at the Rhino version you intend to support.

### `TypeLoadException` for `Rhino.Geometry.X` (or any RhinoCommon type)

Symptoms: plugin assembly fails to JIT a method with `TypeLoadException: Could not load type 'Rhino.Geometry.X'`.

Cause: the plugin was built against a **newer** RhinoCommon than the running Rhino. The type does not exist in the older host's `RhinoCommon.dll`.

Steps:

1. In Visual Studio's Modules window (after attaching), find the loaded `RhinoCommon.dll`. Confirm its version matches the Rhino install.
2. Rebuild the plugin against the matching `RhinoCommon.dll` from the running Rhino's install folder.
3. If supporting both Rhino 7 and Rhino 8, prefer the lowest common API surface, or maintain two build configurations.

### `FileNotFoundException` for `rhcommon_c.dll` / `rhcommon_opennurbs.dll`

Symptoms: at the first RhinoCommon call, `DllNotFoundException` or `FileNotFoundException` for a native helper DLL.

Cause: RhinoCommon's `Rhino.Geometry.*` classes wrap native code in `rhcommon_c.dll` (and friends, including `rhcommon_opennurbs.dll` on some Rhino releases — verify by listing Rhino's `System` folder on your install). These DLLs are present in the Rhino install but not on a generic test environment's PATH. A test runner outside Rhino cannot find them.

Steps:

1. If the failing process is **not** `Rhino.exe`: RhinoCommon is being used outside Rhino. Either run inside Rhino (recommended), or use **Rhino.Inside** to bring up a Rhino runtime in your host process. See `https://developer.rhino3d.com/guides/rhino.inside/`.
2. If the failing process **is** `Rhino.exe`: the install is broken. Run Rhino's `_SystemInfo` command and check for missing native components; reinstall Rhino if needed.
3. For unit tests in the reference plugin StonePack project, the test runner detects this case and skips. See `<project-path>` for the runtime SKIP-on-missing-dll pattern.

### GH document hangs at `Run = true`

Symptoms: a button or boolean toggle wired into the component flips to `true` and Grasshopper freezes; the canvas stops repainting; Rhino's window says "Not Responding".

Cause: the component is doing a long synchronous solve on the UI thread. `SolveInstance` runs on Rhino's UI thread by default, and Grasshopper does not pump messages while a single component is solving.

Fix: convert to `GH_TaskCapableComponent<T>`. Worked example in the reference plugin StonePack project: `<project-path>`. The pattern is:

```csharp
public class IrregularSheetFillComponentAsync : GH_TaskCapableComponent<MyResult>
{
    protected override void SolveInstance(IGH_DataAccess da)
    {
        if (InPreSolve)
        {
            // Snapshot inputs. Do NOT touch da inside the Task body.
            MyInputs inputs = ReadInputsFrom(da);
            CancellationToken ct = default;

            Task<MyResult> task = Task.Run(() => DoLongComputation(inputs, ct), ct);
            TaskList.Add(task);
            return;
        }

        // Post-solve: retrieve the result and write outputs.
        if (!GetSolveResults(da, out MyResult result))
        {
            // Synchronous fallback when async path is disabled.
            MyInputs inputs = ReadInputsFrom(da);
            result = DoLongComputation(inputs, CancellationToken.None);
        }

        WriteOutputsTo(da, result);
    }
}
```

Confirm method names (`InPreSolve`, `GetSolveResults`, `TaskList`) against the RhinoCommon API ref or `mcneel/rhino-developer-samples`.

### Threading bug inside `GH_TaskCapableComponent`

Symptoms: the async component runs but produces wrong outputs, intermittent crashes, or `InvalidOperationException` from a Grasshopper data tree.

Cause: the `Task.Run` body is touching `IGH_DataAccess`, `RhinoDoc.ActiveDoc`, or any other UI-thread-only object. **`IGH_DataAccess` is valid only on the UI thread** and only during the current `SolveInstance` call.

Steps:

1. In `InPreSolve`, snapshot every input you need into plain CLR types (lists, structs, value-type geometry like `Curve.DuplicateCurve()` results).
2. Inside the `Task.Run` body, work only on the snapshot. Never touch `da`, `Document`, `Params`, or any field on the component itself.
3. In the post-solve branch (`!InPreSolve`), call `GetSolveResults`, then write outputs via `da.SetData(...)` / `da.SetDataList(...)` / `da.SetDataTree(...)`.
4. To verify thread identity inside the task: open the Threads window when stopped at a breakpoint in the task body. The thread should not be the main thread (no Eto / WinForms / `RhinoApp` frames at the bottom of the stack). The reference plugin StonePack `IrregularSheetFillComponentAsync.cs` uses this exact pattern.

For the general async-debugging toolbox (Tasks window, Parallel Stacks, `await` that never resumes), defer to the `csharp-debugger` skill.

## reference plugin StonePack-specific cheat references

When Claude is debugging a reference plugin StonePack symptom, these in-repo files are the canonical reference for "how we already solved this":

- `<repo-path>` — canonical `GH_TaskCapableComponent<T>` async pattern (`InPreSolve` snapshot, `Task.Run` body, `GetSolveResults` post-solve, synchronous fallback).
- `<repo-path>` — documents the Rhino right-to-left `Transform` multiplication trap that fixed the "curves off in the distance" bug. Read this before touching any compound-transform code.
- `<repo-path>` — net48-safe `GetHashCode` (no `HashCode.Combine`) pattern. Use this shape when adding new value types in net48 code.
- `<repo-path>` — runtime SKIP detection for `rhcommon_c.dll` / `Grasshopper.dll` not on the load path. Use this shape for any new test runner that may run outside a Rhino install.

## Quick decision tree

```
Plugin won't load?
  _PluginManager status?           -> Disabled / Errored row shows the reason.
  BadImageFormatException?         -> x86 build against x64 Rhino. Set PlatformTarget=x64.
  FileNotFoundException for a DLL? -> Rhino-provided DLL with <Private>true>. Defer to csharp-debugger for <Private> rules.

Plugin loaded, no components?
  GH_AssemblyInfo present?         -> Public parameterless ctor required.
  ComponentGuid unique?            -> Collision drops the second registration silently.
  Exposure visible?                -> Default primary; hidden removes from panel.

Component red on canvas?
  Right-click -> Runtime warnings / errors.
  Mesh / Brep / Curve invalid?     -> IsValidWithLog, Mesh.Check, Curve.IsValid.
  Null input?                      -> Always test da.GetData(...) result.
  Units mismatch?                  -> RhinoMath.UnitScale(from, to). Verify signature.

Wrong geometry, no exception?
  Compound Transform looks reversed -> Rhino multiplies right to left. Build right to left.
  Astronomical numbers (1e+308)?   -> RhinoMath.UnsetValue propagation. Use IsValidNumber.
  ChangeBasis returning identity?  -> Verify Plane validity and overload signature.

GH document hangs at Run=true?
  Convert to GH_TaskCapableComponent<T>. See IrregularSheetFillComponentAsync.cs.

Crash off-thread?
  RhinoCommon mutator off the UI thread.
  Snapshot inputs in InPreSolve, build per-thread, merge on UI thread.

Crash with no repro?
  procdump -ma -e Rhino.exe        -> WinDbg + SOS for net48; dotnet-dump for Rhino on .NET Core.
  Defer the SOS heap walk to the csharp-debugger skill.

MissingMethodException / TypeLoadException after Rhino update?
  ABI drift across Rhino versions. Rebuild against the matching RhinoCommon. Pin the lowest API surface you need.
```

## Verification flags

Several flags, command names, and APIs in this skill are version-sensitive across Rhino 7 and Rhino 8. Confirm with the live source before relying on them in production:

- `_TestStartDebugger` and `RhinoDebugger` Rhino commands: verify with Rhino's `_TestList` command on your installed version. Internal commands change between releases.
- `Rhino.Runtime.HostUtils.RunningOnNetCore` property name and namespace: verify against the RhinoCommon API ref for your Rhino version.
- `Mesh.Check(...)` vs `Mesh.IsValidWithLog(...)` signatures: verify the method that exists on your RhinoCommon version. Older versions exposed different overloads.
- `Brep.IsValidWithLog(out string log)` exact signature: verify against the RhinoCommon API ref.
- `RhinoMath.UnitScale(fromUnits, toUnits)` and `RhinoMath.IsValidNumber(double)`: verify names and signatures against `Rhino.RhinoMath` in the API ref.
- `Transform.ChangeBasis` overload that takes six `Vector3d` arguments: verify parameter order in the API ref before use.
- `RhinoCommon * RhinoCommon` `Transform` multiplication order (right to left): verify in the `Transform` operator overloads section of the API ref.
- `procdump` switches: verify with `procdump.exe /?`. Behavior differs between v9 and v11.
- `corflags`: verify with `where corflags`, then `corflags /?`. Location varies by Windows SDK version.
- `GH_TaskCapableComponent<T>` member names (`InPreSolve`, `GetSolveResults`, `TaskList`): verify against `mcneel/rhino-developer-samples` for your Rhino version, or the Grasshopper SDK reference.
- `rhcommon_opennurbs.dll` presence: verify by listing the `System` folder of your Rhino install. Some Rhino releases consolidate native helpers under different names.

When this skill and a current McNeel doc disagree, the McNeel doc wins. When the McNeel doc and the live behavior on the user's installed Rhino disagree, the live behavior wins for that user — file an issue against `mcneel/rhino-developer-samples` to close the loop.
