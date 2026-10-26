---
name: robotics-ros2-ur
description: Procedure for robot code on Ubuntu with ROS 2 and Universal Robots arms (UR10e with a gripper), including the safety levels from offline generation to hardware, pose and frame rules, URScript waypoint format, unit and TCP checks, ROS 2 build and replay with colcon and ros2 bag, and the handoff from a Grasshopper or Python pose source. Use when an agent writes or reviews ROS 2 nodes, URScript, pose conversion, inverse or forward kinematics, or a simulation run for a UR arm.
compatibility: Claude, Codex, local models, Herdr and Omarchy as clients. Ubuntu 22.04 with ROS 2 Humble or Ubuntu 24.04 with ROS 2 Jazzy. Verify the pairing against the ROS 2 documentation for your installed version.
license: see repository LICENSE
---

# Robotics on ROS 2 with Universal Robots

## Quick start (for small local models)

1. Set the safety level first. Default is Level 1 (offline) or Level 2 (simulation).
2. Write every pose with its units, frame, rotation convention, and TCP offset.
3. Keep the URScript waypoint format: `global WP_n = p[x, y, z, rx, ry, rz]`.
4. Build with `colcon build`. Run the unit tests.
5. Record a `ros2 bag` of the simulation run.
6. Do not run any hardware command. Stop and ask the owner for approval.

Procedure only. Hardware motion is never started by this skill.

## Safety levels (apply first)

| Level | What it means | Default |
|---|---|---|
| 1 | Offline. Code generation and unit tests. No robot connection | Yes |
| 2 | Simulation. Mock controllers or a simulator | Yes, for motion logic |
| 3 | Real hardware. Needs an explicit hardware flag and an approved gate | No |

- Generate code at Level 1. Validate motion at Level 2.
- Never produce Level 3 code without an explicit hardware-enable flag set by the owner.
- Do not run a motion command on hardware from a skill, a script, or an agent step.
- Read-only diagnostics on hardware (joint state, pose snapshots) need the owner's explicit wiring.

## Poses and frames

- Never mix a TCP pose with a motion pose. They are different frames.
- For each pose, state the units (metres or millimetres), the frame (base, tool, TCP, or world),
  the rotation convention (axis-angle, quaternion, or RPY), the waypoint order, and the TCP offset.
- Convert units at one boundary only. Assert the unit at every bridge between tools.
- Keep the gripper's TCP offset in one place, and cite the source of the value.

## URScript waypoints

- Keep the waypoint format `global WP_n = p[x, y, z, rx, ry, rz]`.
- Name waypoints in order. Check the order against the motion plan.
- Generated URScript is reviewed at Level 2 before anything else.

## Reference specifications (manufacturer values)

- UR10e: payload 12.5 kg, reach 1300 mm, repeatability ±0.05 mm.
- RG6 gripper: force-fit payload 6 kg, form-fit payload 10 kg, stroke 150 mm, grip force 25 to 120 N.
- Check these against the current manufacturer datasheets before you use them in a calculation.

## ROS 2 build and test

- Build the workspace with `colcon build`. Source the workspace overlay in each new shell.
- Run unit tests before any node runs against a simulator.
- Keep the ROS 2 distribution, the Ubuntu release, and the driver version in every run record.
- Use a virtual environment for Python tools that do not need ROS. Keep the ROS Python environment
  separate.
- Record a `ros2 bag` for each simulation run you want to replay. Name the bag with the date, the
  scenario, and the commit.

## Handoff from a design tool

- A Grasshopper or Python pose source writes poses to a file in an agreed format. The ROS 2 side
  reads that file. Do not pass poses by copy-paste.
- Check units, frame, and rotation convention at the file boundary, and reject a file that is
  missing any of them.
- Rhino and Grasshopper run on Windows or macOS. Ubuntu reads the exported file.

## Simulation before hardware

1. Level 1: unit tests and a dry run of the URScript generator.
2. Level 2: run the node against a mock controller or a simulator. Replay the bag.
3. Owner review of the bag and the generated URScript.
4. Only then, and only with the owner's explicit approval, a Level 3 gate. This skill does not
   cross that gate.

## Checklist

- [ ] Level stated for each step.
- [ ] Units, frame, rotation, and TCP offset stated for each pose.
- [ ] Waypoint format and order checked.
- [ ] Unit tests pass at Level 1.
- [ ] Simulation run recorded as a bag, with distribution, Ubuntu release, and driver version.
- [ ] No hardware command issued.
