# Simulation campaigns: building-performance studies

The protocol for EnergyPlus-based studies (PCM envelopes, adaptive façades, urban morphology, daylight and glare). Approval gates with the supervisor are part of the method, not an afterthought.

## Pipeline

1. **Read the brief.** Read the proposal and the supervisor's latest written decisions. Restate the case matrix and the fixed versus variable parameters as **tables**, and confirm them.
2. **Confirm inputs before running.** Produce an image or spec sheet of dimensions, parameters and the case matrix, colour-coded as *swept*, *locked to code* or *to confirm*. Send it for approval. Nothing runs on unconfirmed inputs.
3. **Weather.**
   - Baseline: TMYx EPW (climate.onebuilding.org).
   - Future: Future Weather Generator morphing (CMIP6), cross-checked against NASA NEX-GDDP-CMIP6 (reachable through public OPeNDAP), or morph directly from a NEX-GDDP ensemble. CORDEX needs an ESGF login.
   - Urban: Urban Weather Generator (UWG) EPWs from the same context geometry used for the IDFs and figures.
   - Write the weather method, assumptions and limitations into a methods report. Check every EPW's hourly integrity.
4. **Base model.** Make it code-compliant: read values from the actual code documents (SBC 601/602, ASHRAE 90.1/62.1), use representative local operation (for example a Sunday to Thursday work week), and verify the base model on its own first (ASHRAE 140 BESTEST Case 600) before moving to Honeybee or a parametric generator.
5. **Physics and controls.**
   - PCM: EnergyPlus `ConductionFiniteDifference` with `MaterialProperty:PhaseChangeHysteresis` (Honeybee has no native PCM, so inject it through Additional Strings).
   - Use a **fidelity ladder** where coupling matters: L1 bidirectional co-simulation through the Python API, L2 one-way flux injection, L3 native surrogates. Verify one-way against converged coupling.
   - Always include **matched controls**: a no-latent or inert-layer case with only the mechanism of interest disabled. Promote it to a named case in the results table. Run the control; do not reason about it.
   - Test boundary-condition availability against the model's own output (does the night sink you assume actually exist in the model?).
6. **Pilot.** Run a reduced pilot, estimate compute time and send a short proposal with the timings. Run the full campaign only after approval. Stating the cost turns a "let's not" into an approval surprisingly often.
7. **Run.** Launch long campaigns with resumable runners (safe after power loss), in parallel where the machine allows. Write results to JSON or JSONL and record a SHA-256 for every result file. **Frozen results are never re-run casually**; new analyses are additive and first assert that they reproduce the frozen numbers.
8. **Analyse.** Build every figure from result files. Draw geometry to scale with a scale legend, check angles and signs (louvre angles, orientation), and check every value shown in a figure against its data. Use `statistics.median` on unrounded values (`sorted(x)[n//2]` is wrong for even n). A metric pinned at a clamp (`min(1, ·)`) is a bug signal, not a finding.
9. **Report and review.** Write a data-driven experiment report (docx), run a multi-agent journal-reviewer review (about four agents, recomputing from raw data), apply fixes and save a new version. See [manuscript-engineering.md](manuscript-engineering.md).
10. **Package and hand off.** Build the reproducibility package (see [manuscript/reproducibility-and-packaging.md](manuscript/reproducibility-and-packaging.md)) and update `HANDOFF.md`.

## Convergence and uncertainty

- Vary timestep and mesh **separately**: CondFD silently resets a timestep below 20 per hour to 20, and its node spacing depends on the timestep.
- Run uncertainty cases (timestep, grid nodes, ±10% calibration of key properties) and say which conclusions depend on them.
- Do not interpolate a modelled response between cases unless linearity has been shown.

## EnergyPlus traps

- Swapping constructions through EMS needs a dummy CondFD surface with an identical node count.
- An injected `Schedule:File` value cannot be negative: split heat flux into separate gain and loss `OtherEquipment` objects.
- A 1-D PCM side model used for coupling must be implicit to stay stable.
- Do not double-count RunPeriod meters.
- Glare work needs the output variable "Surface Outside Face Incident Beam Solar Radiation Rate per Area".
- The default ground temperature (18 °C) acts as a heat sink; use Kiva for ground contact.
- Windows must face out of the room; adiabatic floors need an explicit construction and the Floor surface type.
- Check constants such as reference floor area against the model, not against the brief.

## Weather-file traps

- **Morphed EPWs can carry the baseline horizontal infrared field unchanged**, which overstates future sky cooling. Check the IR field before any night-ventilation or radiative-cooling analysis.
- The Future Weather Generator jar is large (several GB) and its download host can be intermittent; cache it outside OneDrive.

## Daylight and glare

- Annual metrics: sDA and UDI grids; glare: DGP from Radiance point-in-time or annual runs. Couple daylight to the hourly phase state of PCM glazing and to louvre positions when both change over time.
- Validate ray-traced slat optics against EnergyPlus's ISO 15099 blind model before relying on either.

## Grasshopper and Ladybug Tools

- Document how to run future weather files in Ladybug and how to rebuild an EnergyPlus model in Honeybee as a tech-transfer guide alongside the study, so others in the lab can reproduce it inside Grasshopper.
