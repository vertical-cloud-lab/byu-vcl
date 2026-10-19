# Settings for the OT-2 lid camera stream, read by device.py once at start-up.
# The real file is ~/ac-training-lab/src/ac_training_lab/picam/my_secrets.py on
# the Pi, mode 600, and is never committed: LAMBDA_FUNCTION_URL lets anyone
# create and end broadcasts on the channel.

# The lab's streaming Lambda (vertical-cloud-lab/streamingLambda). Copy the line
# from another stream-cam Pi's my_secrets.py; see README.md.
LAMBDA_FUNCTION_URL = "https://..."

# Appears in the broadcast title: "<WORKFLOW_NAME> stream <CAM_NAME>, <date>".
CAM_NAME = "hqcam-ot2-lid"

# Matched (case-insensitive substring) against broadcast titles to end the
# previous broadcast, and against playlist titles to file the new one.
# "OT2 overhead" files into "OT2 overhead Livestreams Playlist" (PLM4VC4X_7XKQ),
# which the Lambda created for it on 2026-10-19. No hyphen on purpose: with
# "OT-2" in this camera's titles, any camera started as "OT-2" would end them.
WORKFLOW_NAME = "OT2 overhead"

PRIVACY_STATUS = "public"  # "private", "public" or "unlisted"

# Orientation. The flips happen in the sensor readout and cost nothing;
# CAMERA_ROTATION (0, 90, 180, 270) is an ffmpeg filter.
CAMERA_VFLIP = False
CAMERA_HFLIP = False
CAMERA_ROTATION = 0

# A preset ("144p" ... "1080p", all 16:9) or "WIDTHxHEIGHT". The HQ Camera's
# sensor is 4:3, and a 16:9 output crops its field to 16:9, which at 8 mm zoom
# cuts off the front and back rows of deck slots. 4:3 keeps the whole field.
# 1920x1440: YouTube serves this camera's broadcasts live at up to 1440x1080,
# since the Lambda asks for Low latency, which has no 4K. 2160 lines cost
# twice the CPU for nothing more live; see README.md, 2026-10-19.
RESOLUTION = "1920x1440"
FRAME_RATE = 3

# Burn lab local time (top left) into every frame. Forces an ffmpeg re-encode.
TIMESTAMP_OVERLAY = True

# The IMX477's full-field binned mode, which the ISP scales to RESOLUTION.
# Without it libcamera may pick a cropped mode. Above 2028 wide, use the
# full-resolution "4056:3040" (up to 11.7 fps).
SENSOR_MODE = "2028:1520"

# Optional. None or 0 for a sharp picture; see docs/stream-cams.md on main.
PIXELATE_BLOCKS = None

# "yuv420": raw frames to ffmpeg, which does the only encode. The Pi 5 has no
# hardware H.264 encoder, so "h264" would mean two software encodes.
CAMERA_CODEC = "yuv420"

# Only used with CAMERA_CODEC = "h264": the camera encoder's bit rate.
BITRATE = 4000000

# ffmpeg's libx264 encode. "veryfast" halves the upload of "ultrafast" for
# about 1.5x the CPU: 0.65 of a Pi 5 core at 1920x1440 and 3 fps. MAX_BITRATE caps the upload
# (bit/s, 2 s buffer); None leaves it uncapped.
X264_PRESET = "veryfast"
MAX_BITRATE = 4000000
