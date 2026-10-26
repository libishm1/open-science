# Environmental simulation, structure and facades

Part of the computational-design skill. Load this file only for the topic you need. The router is `SKILL.md`.

## Skill 5 — Environmental Simulation (Hot-Arid / Riyadh)

### Design Priorities for Hot-Arid Climate

Generic temperate benchmarks don't apply. Hot-arid design is cooling-dominant.

| Issue | Riyadh Context | Response |
|---|---|---|
| Cooling season | 7–9 months | Minimize solar gain on E/W/roof; maximize thermal mass |
| Solar radiation | 5.5–6.5 kWh/m²/day | External shading mandatory on all orientations except N |
| Glare | High sun altitude + white landscape | Diffuse light preferred; direct sun = glare AND heat |
| Wind | Shamal (NW) prevailing; summer dust | Minimize NW openings; use for night cooling |
| Humidity | 10–30% (low, except coastal) | Evaporative cooling viable; night-flush works |

### Ladybug Tools Stack

```
EPW: SAU_Riyadh.411380_IWEC.epw
       ↓
Ladybug: sun path, radiation rose, wind rose, outdoor thermal comfort (UTCI)
       ↓
Honeybee: daylight (Radiance/DAYSIM), energy (EnergyPlus)
       ↓
Dragonfly: urban-scale UHI, street microclimate
       ↓
Butterfly / Eddy3D: CFD wind
```

### Performance Benchmarks — Hot-Arid

**Energy (ASHRAE 90.1):**
- Office EUI target: <120 kWh/m²/yr (Riyadh, mechanical-dominant)
- High-performance: <80 kWh/m²/yr
- Cooling load for high-performance hot-arid: <15 kWh/m²/yr (aggressive)

**Glazing for Riyadh:**
- North: low-e IGU, U ≤ 1.8 W/m²K, SHGC 0.35–0.45
- South/East/West: SHGC ≤ 0.25; external shading essential
- Summer solar altitude at noon (lat 24.7°N): ≈ 88° — horizontal overhangs nearly ineffective; vertical fins on E/W are more effective

**Daylight:**
- sDA₃₀₀/₅₀% ≥ 55% (LEED v4) — but shade aggressively to control ASE
- ASE₁₀₀₀/₂₅₀h < 10% — critical: direct sun = glare AND heat gain
- Use deep reveals, fritted glass, light shelves to diffuse high-altitude sun

**Outdoor comfort (UTCI):**
- Riyadh summer: UTCI routinely >46°C outdoors (extreme stress)
- Usable outdoor hours: before 9am and after 7pm only without intervention
- Shade + spray cooling required for any usable outdoor space

### Shading Fin Depth Calculation

```python
import math

lat = 24.7  # Riyadh
dec = 23.45  # summer solstice

def solar_altitude(lat, dec, hour_angle):
    lr, dr, hr = map(math.radians, [lat, dec, hour_angle])
    return math.degrees(math.asin(
        math.sin(lr)*math.sin(dr) + math.cos(lr)*math.cos(dr)*math.cos(hr)))

# Worst case: lowest sun on E/W facade during occupied hours
hour_angles = [(h - 12) * 15 for h in range(8, 18)]
min_alt = min(a for h in hour_angles
              if (a := solar_altitude(lat, dec, h)) > 0)

window_height = 1.2  # m
fin_depth = window_height / math.tan(math.radians(min_alt))
print(f"Minimum E/W fin depth: {fin_depth:.2f}m")
```

---

## Skill 6 — Structural Computation

**Form-finding:** Kangaroo 2 (dynamic relaxation), COMPAS TNA (thrust network analysis for masonry vaults), Force Density Method (precise cable nets).

**Karamba3D workflow:** `LineToBeam` → `CrossSection` → `Support` → `Load` → `Assemble` → `Analyze`. Key outputs: `Utilization` (must be <1.0), `MaxDisp`, `BeamForces`.

**Span-to-depth rules:** Steel beam L/20, continuous steel L/25, flat concrete slab L/30, PT slab L/40, timber beam L/15, gridshell R/400–600.

**Topology optimization (SIMP):** E(ρ) = E₀·ρᵖ (p=3). Tools: `Millipede`, `Ameba`. Inputs: design domain, supports, loads, volume fraction target.

---

## Skill 7 — Facade Computation

**Panelization strategies:** Planar quad (PQ mesh, lowest cost) → planar triangle → single-curved → cold-bent glass → double-curved mold (highest cost). Clustering by ±10mm tolerance reduces unique panel types dramatically.

**PQ Mesh:** `Evolute Tools` or `Kangaroo + PlanarizeQuads`. Target planarity: <5mm deviation.

**Hot-arid facade principle:** external shading always outperforms glazing spec. Computational mashrabiya patterns (aperture variation by solar exposure) achieve cultural resonance and performance simultaneously.

---
