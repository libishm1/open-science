# Robotic fabrication: UR arms, ROS2 and Grasshopper bridges

Rules for code and writing about robotic fabrication with Universal Robots arms (UR10e class), OnRobot grippers, ROS2 and Rhino/Grasshopper.

## Trust boundary

All generated code is draft scaffolding. It must be validated in simulation before running on hardware and reviewed against vendor documentation before deployment. The researcher validates it against their specific setup.

Version anchors to verify against current releases: ROS2 Humble (Ubuntu 22.04) or Jazzy (24.04), `ur_robot_driver` 2.x, `ur_rtde` 1.6.x, a MoveIt2 branch matching the distro, Python 3.10+ (Humble) or 3.12+ (Jazzy).

## Reference frame of subsystems

Design (Grasshopper/Rhino) → Bridge → Planning → Execution → Perception. A reference frame, not a mandatory structure.

## Execution ladder

| Level | Meaning |
|---|---|
| 1. Offline | Geometry, IK and toolpaths only |
| 2. Simulation | `use_mock_hardware:=true`, URSim in Docker, MuJoCo or PyBullet |
| 3. Hardware | A real robot |

Default to Level 2 unless hardware execution is explicitly requested. Every program carries a clearly marked gate such as `use_real_hardware: bool = False`. Never produce code that connects to a real robot IP without that gate.

**Minimum motion context before Level 3:** robot IP and type, controller mode (remote or local), TCP offset, payload and centre of gravity, workspace and base frame, pose convention (rotation vector, quaternion or RPY), gripper interface (Modbus, tool I/O or ROS2 topic), real or simulated, ROS2 distro. Stub anything unknown as a parameter with `# TODO: verify`. Never assume values silently.

## Software precautions (these are not functional safety)

1. Check the connection before any motion.
2. Wrap motion in `try/except/finally` with `stopScript()`, `stopJ()` or `stopL()`. These are program halts, not safety-rated stops.
3. Bounds-check targets with `isPoseWithinSafetyLimits()`.
4. Conservative defaults: `speed=0.1`, `acceleration=0.1`.
5. State assumptions in the code.
6. Put a velocity safety-gate node in ROS2 pipelines.
7. The physical e-stop must cut motor power through a hardwired circuit that works with all software dead.

## Diagnostic sequence

1. Powered, and not in protective stop or e-stop.
2. Remote control mode.
3. ExternalControl URCap running.
4. Network reachable (ping).
5. Ports 30001 to 30004 and 50002 open.
6. QoS compatibility between publishers and subscribers (the most common silent failure).
7. `ros2 control list_controllers` shows active controllers.
8. TCP and payload set on the pendant.
9. Calibration extracted and loaded.

## Frames and units

- Name every pose by frame: `<thing>_in_<frame>` with frames such as `base`, `tool0`/`flange`, `tcp`, `world`, `feature`.
- Grasshopper uses millimetres; URScript uses metres. Convert at the bridge, and only there.
- UR axis-angle, ROS quaternions and Grasshopper Planes differ: convert at every bridge boundary.
- three.js is Y-up; Rhino, ROS and IFC are Z-up. Apply an explicit up-axis correction.
- Never mix TCP poses with motion poses. Preserve URScript waypoint format: `global WP_n = p[x, y, z, rx, ry, rz]`.
- Grasshopper Python: identify the runtime first. Legacy GHPython is IronPython 2.7; the Rhino 8 ScriptEditor is CPython 3.

## Failure boundaries

- Do not invent robot specifications; point to the product datasheet. Keep any hard-coded spec as "last verified <date>".
- Do not generate MoveIt2 configurations from memory or assume network topology.
- Do not auto-correct ROS1 to ROS2.
- URScript runs on the controller, not the PC; say so.
- Note the provenance of community or unofficial packages.
- Exported `.script` files must not redeclare a TCP or payload that the gripper's URCap already defines (the symptom is an "installation not found" pendant error). Use the vendor TCP defaults.

## Software design principles

- Dependency inversion: `ArmInterface`, `GripperInterface`, `CameraInterface`, with mock implementations.
- Fail-safe defaults: safety is the default you degrade from, not a feature you add.
- Separate rates: perception 10 to 30 Hz, planning 1 to 10 Hz, control 100 to 500 Hz.
- Configuration over code (YAML).
- Idempotent commands: prefer absolute targets (`move_to(target)`) over relative increments.

## Bridge choices (Grasshopper → robot)

| Approach | Use when |
|---|---|
| rosbridge + WebSocket | Default for Grasshopper ↔ ROS2 |
| FastAPI (uvicorn in the main thread, rclpy in the background) | A custom HTTP API is needed |
| COMPAS FAB | Planning inside the COMPAS ecosystem |
| Direct `ur_rtde` or URScript over port 30002 | No ROS; simple toolpaths |

## Code style

Python with type hints, docstrings and snake_case; C++ with ament_cmake and rclcpp logging; C# (Grasshopper) with RhinoCommon PascalCase; commented URScript; `DeclareLaunchArgument` for every launch parameter.

## Writing about robotic systems

State joint configuration, TCP offset, payload, communication protocol and safety limits in Methods, with verified datasheet values and software versions.
