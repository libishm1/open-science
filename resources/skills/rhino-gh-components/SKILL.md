---
name: rhino-gh-components
description: Procedure for authoring Grasshopper components and definitions - data matching, solve rules, one canonical type per concept, accept-either inputs, synchronous versus asynchronous components, heavy geometry, units and tolerances, and design-grounded citations. Use when writing or reviewing a Grasshopper component, wiring a definition, or choosing sync or async. Windows or macOS only for Rhino steps.
compatibility: Claude, Codex, local models, Herdr and Omarchy as clients. Rhino 8 and Grasshopper run on Windows or macOS. Ubuntu can drive a remote Rhino host.
license: see repository LICENSE
---

# Grasshopper component authoring

## Quick start (for small local models)

1. Check the document units. Use metres for site scale, millimetres for shop scale.
2. Decide the data match (item, list, or tree) before you wire anything.
3. Solve once with Run off. Read the outputs. Read every red message in full.
4. Default new components to synchronous. Use a background task only for a long load, behind a Run gate.
5. Decimate a large mesh once, before any heavy step.
6. Test every output against every plausible input on a real canvas.

Procedure only. Apply it to your own plugins, definitions, and fixtures. Keep results and findings out of shared files.

## 3. Author and solve

- Decide the data match before wiring: item, list, or tree, and the matching type. Grasshopper
  grafts silently when the match is wrong.
- Solve once, then read the outputs. Keep Run inputs off by default, so opening a definition runs
  nothing.
- A component skips its solve when a non-optional input is empty. For either-or inputs, mark the
  alternatives optional, or the second path never runs and only a warning appears.
- Read the red runtime message in full before you change code. Log every failure in the handoff.
- Use absolute paths only.

## 4. Component design

- One canonical type per concept at each component boundary. If you must accept both a custom
  type and a native type, use a generic parameter with a dual-unwrap helper, and report the actual
  type when neither matches.
- Accept the native form and convert internally. The user should not need an extra step.
- Use one ribbon tab per plugin. Group with sub-categories.
- Use meshes, not Breps, for convex polyhedra with planar faces. Triangulate fan-style from the
  first vertex, then compute normals and compact.
- A large one-click component is a facade over the published primitives. It calls the same
  primitives with the same defaults. Keep the primitives available for reuse.
- Before building a component that overlaps a mature external tool, check the tool first. Prefer
  an example workflow that hands the job to it.
- Reuse components. Fork only when tolerances or behaviour differ.
- Put each algorithm's citation in the component's structured attribute and in its hover text.
- Each component serves one named design problem with a stated tolerance and a real fixture. Do
  not ship a demonstration that has no design problem behind it.

## 5. Synchronous or asynchronous

- Default to synchronous.
- Use a background task only for a source or terminal node that loads once and waits, for example a
  large file read or a native solver. Drive it with a Run gate, default false.
- The background task touches plain data only (numeric arrays and point structs). Build every
  geometry object, and run every mesh topology or normal operation, on the UI thread when results
  are emitted.
- Turning Run off cancels the task. The result is discarded when it returns.
- Do not combine a background task with a second full-document solve on each completion. It cascades
  on any upstream change.

## 6. Heavy geometry

- Decimate or remesh a large mesh once, upstream of any heavy operation. Do not loop a reduction
  inside one script; it can exceed the tool's time limit while the work continues on the host.
- For many-cut decomposition, route the cuts through a native CGAL or Geogram backend. Do not fan
  out many RhinoCommon boolean calls on a large mesh.
- Any native entry point that does floating-point work must mask exceptions, or the host crashes.

## 7. Units and tolerances

- Check the document's unit setting before you place anything. Use metres for site, quarry, and
  masonry scale. Use millimetres for shop-scale pieces. Do not mix them in one file.
- Derive tolerances from the characteristic size of the object. A fixed number that works at one
  scale fails at another. The document's default tolerance can be too loose for small parts.
- Keep three quantities separate: numeric epsilon (scaled to size, with a floor), process kerf
  (the tool's cut width), and clearance (a function of size and process).
- Express parameters as fractions of object size, so results compare across scales. Report errors
  as fractions, not raw units.

## Files

- `references/platform-compatibility.md` - where each step runs.
