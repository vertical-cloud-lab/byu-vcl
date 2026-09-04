# 6DOF Robotic Arms & Mobile Bases — Research & Procurement Guide

This document tracks potential 6DOF robotic arm and mobile base options for the BYU Vertical Cloud Lab, including used-market pricing, recommended platforms to watch, and search keywords for alerts.

> **Last updated:** February 2026

---

## Table of Contents

1. [6DOF Robotic Arms](#6dof-robotic-arms)
2. [Mobile Bases](#mobile-bases)
3. [Integrated Mobile Manipulators](#integrated-mobile-manipulators)
4. [Platforms & Marketplaces to Watch](#platforms--marketplaces-to-watch)
5. [Search Keywords & Alerts](#search-keywords--alerts)
6. [Recommendations](#recommendations)

---

## 6DOF Robotic Arms

### Universal Robots (UR3e / UR5e / UR10e)

Industry-standard collaborative arms with excellent ROS/ROS2 support and large ecosystem.

| Model | DOF | Payload | Reach | New Price (USD) | Used Price (USD) |
|-------|-----|---------|-------|-----------------|------------------|
| UR3e  | 6   | 3 kg    | 500 mm  | $23,000–$30,000 | $7,000–$15,000  |
| UR5e  | 6   | 5 kg    | 850 mm  | $30,000–$45,000 | $12,000–$32,000 |
| UR10e | 6   | 10 kg   | 1300 mm | $45,000–$60,000 | $20,000–$38,000 |

- **Pros:** Proven platform, massive community, ROS/ROS2 driver support, extensive accessories (Robotiq grippers, vision systems), collaborative safety rated
- **Cons:** Higher cost; used e-Series holds value well. Older CB3 models are cheaper ($4,000–$12,000) but less supported
- **Used buying tips:** Verify e-Series vs CB3; check included controller + teach pendant; confirm robot hours and software version

### UFactory xArm

Low-cost alternative to UR with strong ROS/ROS2 support. Excellent value for research.

| Model | DOF | Payload | Reach | New Price (USD) | Used Price (USD) |
|-------|-----|---------|-------|-----------------|------------------|
| xArm 6 | 6 | 5 kg   | 700 mm | $8,880–$9,500  | $3,500–$5,000   |
| xArm 7 | 7 | 3.5 kg | 700 mm | $11,000–$11,500 | $7,000–$9,000  |

- **Pros:** Very affordable new price; Python SDK, ROS/ROS2 support; good repeatability (±0.1 mm); active development
- **Cons:** Smaller ecosystem than UR; fewer used units available; less industrial-grade build
- **Where to buy new:** [UFactory US Store](https://www.ufactory.us/xarm), RobotShop, Blue Sky Robotics

### AgileX PiPER

Ultra-affordable 6DOF arm designed for education and research. ROS1/ROS2 native.

| Model | DOF | Payload | Reach | New Price (USD) | Used Price (USD) |
|-------|-----|---------|-------|-----------------|------------------|
| PiPER       | 6 | 1.5 kg | 626 mm | $2,499–$2,799 | Limited availability |
| PiPER L     | 6 | 1.5 kg | 750 mm | ~$3,000–$3,400 | — |
| PiPER H     | 6 | 2 kg   | 636 mm | ~$3,000–$3,400 | — |

- **Pros:** Lowest cost 6DOF option; ~4.2 kg weight (very portable); Python API, ROS1/ROS2; drag teaching; CAN communication
- **Cons:** Low payload (1.5–2 kg); relatively new product so limited used market; less industrial durability
- **Where to buy:** [AgileX official](https://global.agilex.ai/products/piper), RoboBuy, Génération Robots

### Unitree Z1

Lightweight 6DOF arm designed to mount on mobile bases (Unitree quadrupeds or wheeled platforms).

| Model | DOF | Payload | Reach | New Price (USD) | Used Price (USD) |
|-------|-----|---------|-------|-----------------|------------------|
| Z1 Air | 6 | 2 kg   | 740 mm | $11,375–$13,387 | ~$6,900 (rare) |
| Z1 Pro | 6 | 3–5 kg | 740 mm | $10,800–$15,999 | ~$6,900 (rare) |

- **Pros:** Designed for mobile manipulation; force-controlled joints; collision detection; Ubuntu/Ethernet; pairs naturally with Unitree mobile bases
- **Cons:** Smaller community than UR/xArm; primarily designed as mounted arm (no standalone controller box)
- **Where to buy:** RobotShop, Unitree official shop, STEMfinity

### Franka Emika Panda (Franka Research 3)

Premium 7DOF research arm with torque sensors on all joints. Gold standard for manipulation research.

| Model | DOF | Payload | Reach | New Price (USD) | Used Price (USD) |
|-------|-----|---------|-------|-----------------|------------------|
| Panda (Research) | 7 | 3 kg | 855 mm | $27,500–$33,500 | $12,500–$13,000 |
| Panda (Industry) | 7 | 3 kg | 855 mm | — | $5,800+ |

- **Pros:** Best-in-class torque sensing; ±0.1 mm repeatability; ROS/MoveIt integration; extensive research community and publications
- **Cons:** Expensive new; must verify "Research" vs "Industry" version (Industry version has limited programmability); 3 kg payload limit
- **Used buying tips:** Only buy the Research version for full programmability (C++, ROS, FCI access)

---

## Mobile Bases

### Industrial: MiR (Mobile Industrial Robots)

High-end autonomous mobile robots for logistics and research.

| Model | Payload | New Price (USD) | Used Price (USD) |
|-------|---------|-----------------|------------------|
| MiR100 | 100 kg | ~$37,000 | $7,500+ |
| MiR200 | 200 kg | ~$40,000+ | $9,250–$14,000 |
| MiR250 | 250 kg | $20,000–$30,000+ | $15,000+ (est.) |

- **Pros:** Industrial-grade; built-in SLAM and navigation; safety rated; can tow with MiRHook; 10+ hour runtime
- **Cons:** Expensive even used; proprietary software stack (less flexible for custom ROS research); heavy
- **Used buying tips:** Check battery health and charge cycles; confirm software license transfer; verify included charging dock

### Research-Grade: AgileX Mobile Bases

Versatile, ROS-native mobile platforms at various price points.

| Model | Drive Type | Payload | New Price (USD) | Used Price (USD) |
|-------|-----------|---------|-----------------|------------------|
| Scout Mini | 4WD differential | 10 kg | $4,900–$6,900 | ~$6,000 (€) |
| Ranger Mini 3.0 | Omni-directional | 75–120 kg | $15,000–$18,000 | $10,000–$13,000 (est.) |
| LIMO | Multi-mode | 2 kg | $600–$900 | — |

- **Pros:** Full ROS1/ROS2 support; open-source SDK; CAN bus interface; rugged build (Scout/Ranger IP54); multiple drive modes (Ranger)
- **Cons:** Scout Mini has limited payload for arm mounting; Ranger Mini is pricier
- **Best for arm mounting:** Ranger Mini 3.0 (75–120 kg payload supports most 6DOF arms)

### Budget: TurtleBot & Alternatives

Low-cost platforms for basic mobile robotics research.

| Platform | New Price (USD) | ROS2 | Notes |
|----------|-----------------|------|-------|
| TurtleBot3 (Burger/Waffle) | $500–$1,500 | Yes | ROBOTIS; modular; Raspberry Pi/Jetson |
| TurtleBot4 | ~$1,500–$2,000 | Yes | Clearpath/iRobot Create3 base; more integrated |
| Husarion ROSbot 3/XL | $2,500+ | Yes | Professional-grade; turnkey; good documentation |
| SMARTmBOT | ~$210 | Yes | Open-source; 3D-printed; Purdue University project |

### Premium: Clearpath Robotics

Field-proven research platforms (higher cost).

| Platform | Payload | New Price (USD) | ROS2 |
|----------|---------|-----------------|------|
| Dingo | 20 kg | ~$10,000+ | Yes |
| Jackal | 20 kg | ~$20,000+ | Yes |
| Husky | 75 kg | ~$30,000+ | Yes |

- **Pros:** Rugged; outdoor capable; strong academic community; professional support
- **Cons:** Expensive; closed hardware; limited used availability

---

## Integrated Mobile Manipulators

Platforms that combine a mobile base and manipulation arm as a single product.

### Hello Robot Stretch 3

| Feature | Specification |
|---------|--------------|
| Price (new) | $24,950 |
| DOF | 7 (telescopic arm + dexterous wrist) |
| Payload | 2 kg |
| Weight | 24.5 kg |
| Sensors | RealSense cameras, LiDAR |
| Software | ROS2, Python SDK, open-source |

- **Pros:** All-in-one mobile manipulator; lightweight; open source; active research community (Meta, universities); teleoperation ready
- **Cons:** Limited payload (2 kg); specialized form factor; no used market yet
- **Best for:** Embodied AI research, assistive robotics, human-robot interaction

### DIY: Arm + Mobile Base Combos

Build a custom mobile manipulator by pairing components:

| Combo | Estimated Cost (Used) | Notes |
|-------|----------------------|-------|
| AgileX PiPER + Scout Mini | $7,500–$10,000 | Lightweight; both AgileX products; seamless ROS2 integration |
| UFactory xArm 6 + Ranger Mini | $18,000–$23,000 | 5 kg payload arm on 120 kg payload base; serious capability |
| UR3e + MiR200 | $16,000–$46,000 | Industrial-grade mobile manipulation; used pricing highly variable |
| Unitree Z1 + Unitree Go2/B2 | $12,000–$20,000 | Quadruped mobile manipulation; unique locomotion |

---

## Platforms & Marketplaces to Watch

### Used Equipment Marketplaces

| Platform | URL | Best For |
|----------|-----|----------|
| **eBay** | [ebay.com](https://www.ebay.com) | UR arms, MiR robots, Unitree, general surplus |
| **Machinio** | [machinio.com](https://www.machinio.com) | Industrial robots, UR, Franka, wide selection |
| **Surplus Record** | [surplusrecord.com](https://surplusrecord.com) | Used UR and industrial robots |
| **Robots Done Right** | [robotsdoneright.com](https://www.robotsdoneright.com) | Certified used UR robots with warranties |
| **MachineTools.com** | [machinetools.com](https://www.machinetools.com) | UR and other industrial robots |
| **Machineseeker** | [machineseeker.com](https://www.machineseeker.com) | European used robots (MiR, UR, etc.) |
| **Exapro** | [exapro.com](https://www.exapro.com) | Used industrial robots (AgileX Scout, etc.) |
| **resale.info** | [resale.info](https://www.resale.info) | European used robot listings |

### New Equipment Retailers

| Platform | URL | Best For |
|----------|-----|----------|
| **RobotShop** | [robotshop.com](https://www.robotshop.com) | UFactory, Unitree, AgileX, TurtleBot |
| **RoboBuy** | [robobuy.com](https://robobuy.com) | AgileX PiPER, Scout Mini |
| **MYBOTSHOP** | [mybotshop.de](https://www.mybotshop.de) | Franka, AgileX, UFactory (EU) |
| **Génération Robots** | [generationrobots.com](https://www.generationrobots.com) | Franka, AgileX (EU) |
| **Blue Sky Robotics** | [blueskyrobotics.ai](https://www.blueskyrobotics.ai) | UFactory xArm |

### Auction & Surplus

| Platform | Notes |
|----------|-------|
| **GovPlanet / GovDeals** | Government surplus; occasionally has industrial robots |
| **Bidspotter** | Industrial auction aggregator |
| **HiBid** | Online auction platform |
| **University surplus sales** | Check neighboring university surplus departments |

---

## Search Keywords & Alerts

Set up saved searches and email alerts on eBay, Machinio, and other platforms using these keywords:

### Robotic Arms
- `UR3e robot` / `UR5e robot` / `UR10e robot`
- `Universal Robots collaborative` / `Universal Robots cobot`
- `UR3 CB3` / `UR5 CB3` (for older, cheaper models)
- `UFactory xArm` / `xArm 6` / `xArm 7`
- `AgileX PiPER` / `PiPER robotic arm`
- `Unitree Z1` / `Unitree Z1 Pro`
- `Franka Emika Panda` / `Franka Research 3`
- `6DOF robot arm` / `6 axis robot arm`
- `collaborative robot arm` / `cobot arm`
- `robotic arm ROS` / `research robot arm`

### Mobile Bases
- `MiR100` / `MiR200` / `MiR250` / `MiR mobile robot`
- `AgileX Scout Mini` / `AgileX Ranger Mini`
- `Clearpath Jackal` / `Clearpath Dingo` / `Clearpath Husky`
- `TurtleBot` / `TurtleBot3` / `TurtleBot4`
- `mobile robot base ROS`/ `AMR autonomous mobile robot`
- `AGV automated guided vehicle`
- `Husarion ROSbot`

### Mobile Manipulators
- `Hello Robot Stretch` / `Stretch 3 robot`
- `mobile manipulator` / `mobile manipulation robot`
- `robot arm mobile base`

### General (catch-all)
- `used collaborative robot` / `used cobot`
- `surplus robot arm` / `refurbished robot`
- `6 axis cobot used`
- `research robot used`

---

## Recommendations

### Best Value (Budget ~$3,000–$5,000)

**AgileX PiPER + LIMO or Scout Mini**
- Total: ~$3,100–$9,700 (new)
- Gets you a 6DOF arm and mobile base with full ROS2 support
- Good starting point for mobile manipulation research
- Limitation: Low payload (1.5 kg arm)

### Best Used Deal to Watch For

**Used UFactory xArm 6** (~$3,500–$5,000 used)
- Best price-to-capability ratio on used market
- 5 kg payload, 700 mm reach, ROS/ROS2
- Pair with an AgileX Ranger Mini for serious mobile manipulation

### Best All-Around (Budget ~$10,000–$15,000)

**Used UR3e** (~$7,000–$12,000 used)
- Industry standard with massive community support
- Pair with an AgileX Scout Mini for mobile capability
- Can also operate as a standalone tabletop arm

### Best Integrated Solution

**Hello Robot Stretch 3** ($24,950 new)
- No assembly required; ready for mobile manipulation research out of the box
- Strong community; used by leading AI labs
- Worth the premium if budget allows

### Best for Heavy-Duty Research

**Used UR5e or UR10e + Used MiR200**
- Total used: ~$20,000–$45,000
- Industrial-grade mobile manipulation
- 5–10 kg arm payload on a 200 kg mobile base

---

*This document should be updated as new listings and products become available. Set up saved search alerts on eBay, Machinio, and Surplus Record to catch deals early.*
