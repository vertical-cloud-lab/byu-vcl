# How much RAM the wrist Pi 5 needs (8 October 2026)

The lab's spare Pi 5s are 1 GB boards. This page asks whether the wrist Pi should be bigger, if
it's going to run Claude Code, OpenCV, YOLO, U-Net or Mask R-CNN on the arm itself. Storage isn't
the question here, since that's the SD card.

## Short answer

**Buy the 8 GB board ($175 at PiShop.us, in stock).** The 4 GB ($110) meets Claude Code's stated
minimum, but not with the cameras and a PyTorch model running beside it. Below 4 GB, Claude Code
is out, and 1 GB is already tight for the two cameras alone.

| Pi 5 | PiShop.us, 8 Oct 2026 | What fits, from the measurements below |
|---|---|---|
| 1 GB | $45, out of stock (the lab has spares) | Both cameras plus OpenCV or AprilTags, headless, with little to spare. On the CubXL's 1 GB Pi, one of two 12 MP cameras timed out on 5 of 6 captures, most likely for lack of memory ([#171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5688528247)). No Claude Code |
| 2 GB | $77.50, out of stock | The cameras plus YOLO11 through ONNX Runtime or NCNN (150–450 MB). A PyTorch model too, but no Claude Code: its docs ask for 4 GB |
| 4 GB | $110, in stock | Claude Code, or one of the PyTorch models (U-Net, Mask R-CNN on a shrunk frame) beside the cameras. Not all of them at once (about 3.4 GB) |
| **8 GB** | **$175, in stock** | All of the above at once, with room for page cache, `pip install`, builds and Docker. Also a small local language or vision–language model (a 3B model at 4-bit is about 2 GB) |
| 16 GB | $305, in stock | Only for local 7–8B language models. Not needed for vision |

The prices are well above the launch list prices ($60 for 4 GB and $80 for 8 GB in 2023), so check
other stores before ordering.

**The harder limit for advanced vision is speed, not memory.** A Pi 5's CPU runs YOLO11n at about
7 frames a second and Mask R-CNN at roughly one frame every 10 to 15 s. For more than that, add an
AI HAT+ rather than more RAM (see [Speed](#speed)).

## Measured memory

[`ram_footprint.py`](ram_footprint.py) runs each workload in its own fresh Python process and
records its peak resident memory. Results are in [`ram_footprint.json`](ram_footprint.json).

- **Where it ran:** the CI runner (x86_64, 4 CPUs, Xeon Platinum 8573C), with Python 3.12, PyTorch
  2.14.1, ONNX Runtime 1.30.0, NCNN 1.0.20260526, Ultralytics 8.4.174 and OpenCV 5.0.0.
- **Why that's fair:** weights and activations are the same size on an ARM CPU, so these peaks
  carry over to a Pi 5 to within the frameworks' own overhead, tens of MB.
- **The frames** are both cameras at full size: the HQ's 4056 × 3040 and the Wide's 4608 × 2592.

| Workload | Peak memory |
|---|---|
| Raspberry Pi OS Lite (Debian 13), idle: the CubXL Pi 5, 1 GB, with Tailscale, NetworkManager and Raspberry Pi Connect | 269 MB used, 721 MB available |
| Claude Code 2.1.293, this session on the runner, after about 28 min | 375 MB peak, 313 MB now |
| OpenCV: AprilTags (36h11) on both full frames, a bench scene with 12 tags each | 268 MB. All 24 tags found |
| The same on frames of pure noise, a detector's worst case | 687 MB |
| PyTorch and torchvision, just imported | 305 MB |
| YOLO11n detect, 640: Ultralytics (PyTorch) / ONNX Runtime / NCNN | 493 / 155 / 148 MB |
| YOLO11s detect, 640: Ultralytics / ONNX Runtime | 564 / 263 MB |
| YOLO11m detect, 640: ONNX Runtime | 444 MB |
| YOLO11n-seg (instance segmentation), 640: Ultralytics / ONNX Runtime / NCNN | 508 / 194 / 159 MB |
| U-Net with a ResNet-34 encoder, 512 × 512, PyTorch | 595 MB |
| Mask R-CNN (ResNet-50 FPN v2), PyTorch, frame shrunk to 1066 × 800 first | 1.28 GB |
| Mask R-CNN, the full 12 MP frame passed in | **10.3 GB** |

What the table shows:

- **Shrink frames before Mask R-CNN.** The model works at 800 px either way, but it pastes each mask
  back at the input's size: 100 masks × 12 MP × 4 bytes is about 5 GB. With untrained weights it
  returns its maximum of 100 detections (checked), so both Mask R-CNN rows are the top end for a
  real scene.
- **Export YOLO to NCNN or ONNX on the Pi.** PyTorch alone costs about 300 MB before any model
  loads. Exported, the same YOLO11n needs a third as much memory, and NCNN is also the fastest
  format on a Pi 5 (Ultralytics' benchmarks).
- **The camera stack comes on top.** These numbers include each process's own copy of the frames,
  but not libcamera's buffers. By arithmetic, not measured: one full-size RGB frame plus its raw
  frame is about 48 MB per camera per buffer. That's about 100 MB for both cameras with one buffer
  each, and 400 MB when streaming with four.
- **Claude Code itself** is small (about 0.4 GB), but what it runs isn't. A `pip install` of PyTorch,
  a C++ build or a test suite each want hundreds of MB to a few GB, on top of everything else.

Adding it up for one example, everything asked about running at once:

| | MB |
|---|---|
| OS, idle | 270 |
| Both cameras streaming, four buffers each (estimate) | 400 |
| Claude Code | 375 |
| YOLO11n-seg in PyTorch | 508 |
| U-Net | 595 |
| Mask R-CNN on a shrunk frame | 1,279 |
| **Total** | **about 3,400** |

A 4 GB Pi 5 has about 4,000 MB to hand out (the 1 GB one shows 990), so that's within about
0.6 GB of full, with no page cache, no build and nothing else running. That's the case for 8 GB.
Exporting YOLO11n-seg to NCNN would save 350 MB of it.

## Speed

From published benchmarks, not run here, all at 640 × 640 unless stated otherwise:

| Model | Pi 5 CPU | AI HAT+ 13 TOPS (Hailo-8L) | AI HAT+ 26 TOPS (Hailo-8) |
|---|---|---|---|
| YOLO11n detect | 6.8 fps in ONNX ([Ultralytics](https://docs.ultralytics.com/guides/raspberry-pi/)). YOLO26n is 67 ms (15 fps) in NCNN | 157 fps | 185 fps |
| YOLO11s detect | | 92 fps | 111 fps |
| YOLO11n-seg | | 149 fps | |
| YOLO11m-seg | | 24 fps | |

- **Where the Hailo figures come from:** the
  [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo) v2.19.0 tables, at batch size 1.
  A camera feeding the HAT gets less than that, since it also waits on capture and pre-processing.
- **Scaling the runner's times to a Pi 5:** YOLO11n in ONNX took 43.5 ms on the runner and takes
  147 ms on a Pi 5, a factor of about 3.4. On that basis, very roughly:
  - U-Net (ResNet-34, 512 × 512, PyTorch) is about 1.2 s per frame on a Pi 5.
  - Mask R-CNN on a shrunk frame is about 14 s per frame (4.1 s on the runner).

What that means for each kind of model:

- **YOLO and instance segmentation on the CPU** (YOLO11n or YOLO11n-seg in NCNN): a few to 15
  frames a second. That's enough for checking a grasp between moves, but not for tracking during one.
- **U-Net-style segmentation** is fine on the CPU at about a frame a second, or faster on a HAT once
  it's compiled with Hailo's tools.
- **Mask R-CNN** is impractical on a Pi. YOLO11-seg gives instance masks at 150 fps on the 13 TOPS
  HAT, so use that instead.
- **The AI HAT+ boards** cost $76.95 (13 TOPS) and $119.95 (26 TOPS) at PiShop.us.
  - The Hailo runs the network, so the Pi needs little RAM for it.
  - It needs models compiled for the Hailo. The model zoo has the common ones; a custom U-Net needs
    Hailo's Dataflow Compiler on a PC.
  - It stacks on the GPIO header above the Active Cooler and connects by the PCIe ribbon. The
    carrier's CAD doesn't leave room for it yet.
  - It also draws from the Pi's 5 V, which makes the power question harder, not easier
    ([`../power/README.md`](../power/README.md)).
- **The AI HAT+ 2** ($200) uses a Hailo-10H with its own 8 GB. It's for running language and
  vision–language models on the device. For vision alone, PiShop's listing says it matches the
  26 TOPS HAT.
- **The Raspberry Pi AI Camera** ($74.95) runs a small network on the sensor itself. It would
  replace one of the mount's cameras, not add to them, so it's a different design.

## Claude Code on the Pi

- **Supported:** Claude Code's [system requirements](https://code.claude.com/docs/en/setup)
  are "4 GB+ RAM, x64 or ARM64 processor" on Debian 10 or newer, so a Pi 5 running Raspberry Pi OS
  qualifies. The native installer and the `linux-arm64` npm package both cover it.
- **Memory:** this session's own process peaked at 375 MB. It runs the model in the cloud, so the
  rest of the board is free for the cameras and whatever Claude Code runs.
- **A 1 or 2 GB board would run it below the documented minimum.** It would also swap to the SD
  card the first time it installs or builds something.

## Not done

- **Nothing was run on a Pi 5 except the idle memory reading.** Running the benchmark on the
  CubXL's 1 GB Pi needs PyTorch installed on a working instrument, so I didn't. It can be done
  with `python compute/ram_footprint.py prep && python compute/ram_footprint.py all`.
- **The camera buffer figure is arithmetic.** Measuring it means streaming both cameras on a Pi.
- **The Pi 5 times are scaled from one benchmark,** apart from the published rows.
