# Design framing: top-down and bottom-up

Part of the computational-design skill. Load this file when a task asks which design flow a
component, workflow, or example serves.

## Definitions

- **Top-down.** Design the final form first. Split it into parts. Find or cut material that
  matches each part.
- **Bottom-up.** Start from the material as it is. Let the form emerge from its properties
  (grain, edge, weight, vein, size distribution).

The distinction is whose form leads: the designer's or the material's. Both flows matter. Keep both
first-class in any tool.

## Examples (generic)

| Flow | Example |
|---|---|
| Top-down | Arch or vault designed first, decomposed into voussoirs, each matched to a stock block |
| Top-down | A sculpted surface designed first, with blocks sized to carve it |
| Top-down | A form built from platonic solids, then filled with matching units |
| Bottom-up | Rubble wall built from the pieces available on site |
| Bottom-up | Planks edge-matched along their natural edges, so the seams are the design |
| Bottom-up | Mosaic assembled from irregular fragments inside a closed boundary |
| Bottom-up | Tiles placed so that veins or grain flow across joints |

## Working rules

1. Ask: does this serve the top-down flow, the bottom-up flow, or both?
2. Do not confuse "starts from inventory" with bottom-up. The test is whether the form adapts to the
   material or the material is forced to the form.
3. Top-down needs a fit search: for each designed part, find the inventory item that fits within a
   stated tolerance.
4. Bottom-up needs inventory data (dimensions, shape, properties) and an assembly rule that uses it.
5. State the flow in the component description and in the example's notes.
