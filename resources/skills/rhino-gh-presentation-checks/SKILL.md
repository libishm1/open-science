---
name: rhino-gh-presentation-checks
description: Procedure for making Grasshopper examples and results presentable and checkable - self-presenting final forms, hidden previews before capture, small captures, numbered saves that never overwrite, cold-reopen acceptance, live validation and the pre-ship checklist. Use when preparing a shipped example, capturing a result from Rhino, or checking a definition before handoff.
compatibility: Claude, Codex, local models, Herdr and Omarchy as clients. Rhino 8 and Grasshopper run on Windows or macOS. Ubuntu can drive a remote Rhino host.
license: see repository LICENSE
---

# Grasshopper presentation and validation

## Quick start (for small local models)

1. Make the final form appear on the canvas. Do not use a script to create it.
2. Hide the component previews before a capture.
3. Capture a small image (about 620 pixels wide). Read the downscaled image.
4. Save each build as a new numbered file with a short note. Never overwrite a working build.
5. Reopen the file cold. Check that the final form appears without any script.
6. Mark the item done only after the owner checks it on a real canvas.

Procedure only. Apply it to your own plugins, definitions, and fixtures. Keep results and findings out of shared files.

## 8. Presentation and examples

- The final form appears on the canvas. Use custom preview and gradient components for colour,
  and move, rotate, or orient components for layout. Hide the raw component previews so the custom
  previews own the look.
- Scripts are for headless capture only: baking copies, capturing images, or setting persistent
  data. They are never the step that creates the final visible form.
- Acceptance check: reopen the file cold. Does the capture appear without any script?
- Validate live. Open the file, solve it, confirm the preview has geometry, and confirm no runtime
  errors. Wiring alone does not count.
- Wire every output to every plausible input on a real canvas before you call a plugin finished.
  Headless tests cannot catch conversion failures.
- Do not auto-wire the preview to "the first mesh output". Pick the terminal geometry output and
  check that it carries data on solve.
- Do not add a stability or verification component blindly. On an unsettled input it can report a
  spurious failure that looks like a broken example.

## 9. Captures and saves

- Hide component previews before a viewport capture. Otherwise baked geometry picks up preview
  colours.
- Use shaded display for flat or uncoloured fixtures. Use a light background for diagnostic views.
- Keep image width below the tool's payload limit (about 620 pixels wide, if the JSON cap applies).
  Read downscaled images, not full-resolution ones.
- Show intermediate results often, not only at the end. Bake, capture, and read after each
  substantive solver result, and colour by the metric.
- Save each build as a new numbered file with a short companion note: what changed, layer counts,
  key parameters, and remaining gaps. Never overwrite or delete a working build.
- Save through the document I/O object. Before saving, copy the document and remove the bridge
  component from the copy, so the file has no missing-component placeholder. Do not remove the
  bridge from the live document.

## 10. Checklist before a plugin or example ships

- [ ] Loaded version verified in the running process, not only on disk.
- [ ] One copy of each plugin in the scanned folders.
- [ ] Every component solves from a cold open with Run off.
- [ ] Every output wired to every plausible input on a real canvas.
- [ ] Final form visible without a script; reopened cold.
- [ ] Units set and checked; tolerances derived from size.
- [ ] Algorithm citation in the hover text.
- [ ] Numbered save written with its note.
- [ ] Visual check by the owner on a real Rhino canvas.

## Files

- `references/platform-compatibility.md` - where each step runs.
