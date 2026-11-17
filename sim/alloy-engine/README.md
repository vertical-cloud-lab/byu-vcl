# Alloy physics engine, tried on lab hardware (#351)

Work in progress for [#351](https://github.com/vertical-cloud-lab/byu-vcl/issues/351): trying
[Alloy](https://alloy.argonrobotics.ai/) (`pip install alloy-engine`, 0.1.6), Argon Robotics' multi-material physics
engine for robot learning, on things from this lab. Everything here ran on a GitHub Actions runner's CPU (4 cores,
no GPU).

- `vlm_tray.py`: loose labware on a vertical lift module tray that speeds up and stops, in many parallel worlds.
