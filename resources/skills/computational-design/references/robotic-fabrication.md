# Robotic fabrication

Part of the computational-design skill. Load this file only for the topic you need. The router is `SKILL.md`.

## Skill 10 — Robotic Fabrication

> **Stack split:** For UR10e + RG6 + ROS2 specifics (ur_rtde, MoveIt2, FastAPI bridge, QoS matrices, Docker-compose, ROS2 action servers), use the `robotics-in-architecture` skill. This section covers fabrication concepts, robot selection, Grasshopper plugins, motion types, and native robot languages — applicable across all brands.

### Robot Selection Reference

| Robot | Reach (mm) | Payload (kg) | Repeatability (mm) | AEC Use |
|---|---|---|---|---|
| **UR10e** *(primary stack)* | 1300 | 12.5 | ±0.03 | Light assembly, collaborative, lab fab |
| UR16e | 900 | 16 | ±0.03 | Heavier collaborative tasks |
| ABB IRB 4600-60 | 2050 | 60 | ±0.05 | Milling, medium assembly |
| ABB IRB 6700-235 | 2650 | 235 | ±0.05 | Heavy assembly, large milling |
| KUKA KR 120 R2700 | 2701 | 120 | ±0.05 | General fabrication |
| KUKA KR 210 R3100 | 3100 | 210 | ±0.06 | Timber assembly, large components |
| Fanuc M-20iD/25 | 1831 | 25 | ±0.02 | Precision assembly, welding |
| Fanuc M-710iC/50 | 2050 | 50 | ±0.07 | General fabrication |

**Repeatability vs. Accuracy:** Repeatability (±0.03–0.08mm) = how consistently the robot returns to a taught point. Accuracy (±0.2–2.0mm) = how close it gets to a commanded Cartesian point. Accuracy is worse due to kinematic model errors and backlash. Calibration improves accuracy to ±0.2–0.5mm.

**Payload includes end effector mass.** Check both mass AND moment of inertia at the tool flange — capacity decreases with distance from J6 axis.

### End Effectors

| Effector | Application | Notes |
|---|---|---|
| Spindle (HSD, Hiteco) | Robotic milling (foam, timber, GFRP) | 1–24kW, 1k–40k RPM; needs ATC for multi-tool |
| Extruder (auger/piston) | Concrete/clay/polymer printing | Temperature-controlled for thermoplastics |
| Gripper (parallel/vacuum) | Pick-and-place: bricks, panels, timber | Vacuum for flat panels; mechanical for irregular |
| Hot-wire cutter | EPS/XPS foam cutting | Wire temp 200–400°C; smooth foam surfaces |
| Welding torch (MIG/MAG) | WAAM steel nodes, structural welding | Fronius CMT preferred for WAAM |
| **OnRobot RG6** *(primary stack)* | Collaborative gripping; adaptive fingers | ±0.1mm repeatability; 0–160mm stroke |

### Grasshopper Plugins (Multi-Brand)

**HAL Robotics** (multi-brand — ABB, KUKA, UR, Fanuc, Staubli):
- Procedure + Target + Solver components in GH
- Inverse kinematics, collision detection, singularity checking
- Exports to RAPID, KRL, URScript, and others
- Real-time control mode for adaptive fabrication

**KUKA|prc** (KUKA-specific):
- LIN / PTP / CIRC / SPLINE motion commands
- I/O control for end effectors; SRC/DAT file generation
- Virtual 7th axis (linear track) support

**Robots by Visose** (open-source, multi-brand):
- Supports ABB, KUKA, UR, Fanuc, Staubli
- Robot cell → target generation → simulation → native code
- Flexible architecture; good for research and teaching

### Motion Types (All Brands)

| Motion | Path | Use |
|---|---|---|
| PTP / MoveJ / movej | Joint space; not straight line in Cartesian | Large repositioning moves |
| LIN / MoveL / movel | Straight line in Cartesian | All fabrication operations |
| CIRC / MoveC / movec | Arc through via point | Circular toolpaths |
| SPLINE | Smooth continuous | Extrusion, painting, continuous processes |

**Singularity types:** Overhead (J5=0), Extended (full reach), Base (TCP above J1). Avoid by: offsetting tool orientation ≠ 0° at J5, limiting workspace from full extension, using PTP through singular zones.

### Coordinate Systems

- **World** — fixed workcell reference; all frames reference this
- **Base** — origin at J1; differs from World if robot is on a track
- **TCP (Tool)** — active end-effector point; must be calibrated precisely
- **Workpiece / Work Object** — part coordinate system; defined by 3-point touch-up on physical workpiece
- **User Frame** — arbitrary reference for organizing targets across multiple workpieces

### Native Robot Languages

**URScript (UR10e — primary stack):**
```python
def main():
  set_tcp(p[0, 0, 0.200, 0, 0, 0])          # TCP 200mm from flange
  movej([0,-1.57,1.57,-1.57,-1.57,0], a=1.0, v=0.5)   # home
  movel(p[0.5, 0.0, 0.3, 0, 3.14, 0], a=0.5, v=0.2)   # approach
  movel(p[0.5, 0.1, 0.05, 0, 3.14, 0], a=0.3, v=0.1)  # fab start
  movel(p[0.6, 0.1, 0.05, 0, 3.14, 0], a=0.3, v=0.1)  # fab end
  movel(p[0.5, 0.0, 0.3, 0, 3.14, 0], a=0.5, v=0.2)   # retract
  movej([0,-1.57,1.57,-1.57,-1.57,0], a=1.0, v=0.5)   # home
end
# p[x,y,z,rx,ry,rz] in meters + axis-angle radians
# a = acceleration (m/s²), v = velocity (m/s)
```

**RAPID (ABB):**
```rapid
PROC main()
  MoveJ pHome, v1000, z50, myTool;
  MoveL pApproach, v500, z10, myTool \WObj:=myWobj;
  MoveL p1, v100, fine, myTool \WObj:=myWobj;  ! fine = stop exactly
  MoveL p2, v100, fine, myTool \WObj:=myWobj;
  MoveL pApproach, v500, z10, myTool \WObj:=myWobj;
  MoveJ pHome, v1000, z50, myTool;
ENDPROC
! v100 = velocity mm/s | z10 = blend radius mm
```

**KRL (KUKA):**
```krl
DEF main()
  $TOOL = TOOL_DATA[1]
  $BASE = BASE_DATA[1]
  $VEL.CP = 0.5   ; m/s Cartesian
  PTP HOME
  LIN {X 500, Y 0,   Z 200, A 0, B 90, C 0}
  LIN {X 500, Y 100, Z 50,  A 0, B 90, C 0} C_DIS  ; C_DIS = blend
  LIN {X 600, Y 100, Z 50,  A 0, B 90, C 0} C_DIS
  LIN {X 500, Y 0,   Z 200, A 0, B 90, C 0}
  PTP HOME
END
```

### AEC Robotic Applications

| Application | Brands Used | Notes |
|---|---|---|
| Robotic milling (foam, timber) | KUKA, ABB | Extended reach; high payload for spindle |
| Collaborative assembly | UR10e, UR16e | ISO/TS 15066 force limits; no fencing required |
| Concrete/clay printing | ABB, KUKA, custom | Extruder end effector; path = Grasshopper contour |
| WAAM steel nodes | Fanuc, ABB | Fronius CMT torch; wire feedstock |
| Bricklaying | UR, KUKA | Vacuum or mechanical gripper; adhesive dispenser |
| Hot-wire foam cutting | UR, custom | Wire on 2-point frame; ruled surface toolpaths |
| Fiber winding | KUKA, ABB | ICD/ITKE pavilion method; anchor-to-anchor paths |

### File-to-Factory Pipeline

```
Grasshopper geometry (toolpath curves)
       ↓
Target frames (Plane per point: position + normal = TCP orientation)
       ↓
Robot plugin (HAL / KUKA|prc / Robots): IK solve + collision check
       ↓
Simulate in GH (verify reach, singularities, joint limits)
       ↓
Export native code (URScript / RAPID / KRL / Fanuc TP)
       ↓
Upload to controller (TCP/IP network for UR; FTP/USB for KUKA/ABB)
       ↓
Air-cut dry run → scrap trial → production
```

### Pre-Flight Checklist

Before running any robot program:
1. Geometry verified in simulation — no collisions, no singularities
2. TCP calibrated and matches program definition
3. Workpiece zeroed — touch-up on physical workpiece matches workobject definition
4. Payload set in controller — mass + center of gravity
5. Velocity limited for first run (25–50% of programmed speed)
6. Safety perimeter clear; E-stop accessible
7. Dry run at reduced speed with spindle/effector off
8. First article on scrap material before production run

**For UR10e ROS2/ur_rtde integration** → see `robotics-in-architecture` skill.

---
