import json
import os
import re
import shutil
import subprocess

import requests
from my_secrets import (
    CAM_NAME,
    CAMERA_HFLIP,
    CAMERA_ROTATION,
    CAMERA_VFLIP,
    FRAME_RATE,
    LAMBDA_FUNCTION_URL,
    PRIVACY_STATUS,
    RESOLUTION,
    TIMESTAMP_OVERLAY,
    WORKFLOW_NAME,
)

# Optional setting; older my_secrets.py files may not define it.
try:
    from my_secrets import SENSOR_MODE
except ImportError:
    SENSOR_MODE = None

# Optional setting; older my_secrets.py files may not define it.
try:
    from my_secrets import PIXELATE_BLOCKS
except ImportError:
    PIXELATE_BLOCKS = None

# Optional setting; older my_secrets.py files may not define it. The bit rate
# of the camera's own H.264 encoder, before ffmpeg re-encodes. 1 Mbit/s is
# fine up to 480p; a 1080-line picture needs about 4 Mbit/s or it arrives blocky.
try:
    from my_secrets import BITRATE
except ImportError:
    BITRATE = None

# Optional setting; older my_secrets.py files may not define it.
# "h264": the camera encodes and ffmpeg re-encodes only if filters are on.
#   On a Pi with no hardware encoder (Pi 5), rpicam-vid encodes in software
#   through libav, which needs "--libav-format h264" and writes to "pipe:1".
# "yuv420": raw frames to ffmpeg, which does the only encode. No second
#   encode and no intermediate bit rate, at the cost of ffmpeg always
#   re-encoding. Each row arrives padded to a multiple of 128 pixels
#   (2880 wide comes as 2944); ffmpeg reads the padded width and crops.
try:
    from my_secrets import CAMERA_CODEC
except ImportError:
    CAMERA_CODEC = "h264"

# Optional settings; older my_secrets.py files may not define them. They
# apply whenever ffmpeg encodes (filters on, or CAMERA_CODEC = "yuv420").
# X264_PRESET: libx264's speed/size trade-off. "ultrafast" suits a Zero 2 W;
#   on a Pi 5 at 2160 lines and 3 fps, "veryfast" halves the upload.
# MAX_BITRATE: optional cap in bit/s (VBV, with a 2 s buffer); None leaves
#   libx264's constant-quality default uncapped.
try:
    from my_secrets import X264_PRESET
except ImportError:
    X264_PRESET = "ultrafast"
try:
    from my_secrets import MAX_BITRATE
except ImportError:
    MAX_BITRATE = None

# Optional settings; older my_secrets.py files may not define them.
# CAMERA_SOURCE: "rpicam-vid", as on every other picam, or "picamera2": picam_source.py
#   next to this file, one picamera2 process that writes the same raw frames
#   (needs CAMERA_CODEC = "yuv420") and, while the stream runs, serves
#   full-resolution stills on 127.0.0.1:STILL_PORT. That is option A of
#   borysgroup/streamingLambda#9: rpicam-still can't open a camera that
#   rpicam-vid holds, but one process can serve both from the same frames.
# STILL_SIZE: "WIDTHxHEIGHT" of those stills; None for the sensor mode's size.
# SETUP_OVERLAY: draw a centre cross and the live focus score on the stream,
#   for lining the camera up and focusing it (picamera2 source only).
# SETUP_BOX: (width, height) as fractions of the picture: with the setup
#   overlay, a centred box where the plate's outline should land once the zoom
#   is right. (0.927, 0.828) leaves 5 mm of deck either side of a 96-well
#   plate (../../cad/setup_video.py, target_zoom). None for no box.
try:
    from my_secrets import CAMERA_SOURCE
except ImportError:
    CAMERA_SOURCE = "rpicam-vid"
try:
    from my_secrets import STILL_PORT
except ImportError:
    STILL_PORT = 8081
try:
    from my_secrets import STILL_SIZE
except ImportError:
    STILL_SIZE = None
try:
    from my_secrets import SETUP_OVERLAY
except ImportError:
    SETUP_OVERLAY = False
try:
    from my_secrets import SETUP_BOX
except ImportError:
    SETUP_BOX = None

# Where picam_source.py writes the focus score for the overlay (tmpfs).
OVERLAY_FILE = "/dev/shm/picam-overlay.txt"

# Resolution mappings for YouTube-compatible resolutions
RESOLUTION_MAP = {
    "144p": (256, 144),
    "240p": (426, 240),
    "360p": (640, 360),
    "480p": (854, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
}


def get_camera_command():
    """
    Returns the available camera command.

    Uses 'rpicam-vid' on trixie or 'libcamera-vid' on bookworm.
    """
    if shutil.which("rpicam-vid"):
        return "rpicam-vid"
    elif shutil.which("libcamera-vid"):
        return "libcamera-vid"
    else:
        raise RuntimeError(
            "Neither 'rpicam-vid' nor 'libcamera-vid' command found on this system"
        )


def start_stream(
    ffmpeg_url,
    width=854,
    height=480,
    rotation=0,
    framerate=15,
    timestamp_overlay=False,
    sensor_mode=None,
    pixelate_blocks=None,
    bitrate=None,
    codec="h264",
    x264_preset="ultrafast",
    max_bitrate=None,
    camera_source="rpicam-vid",
    still_port=8081,
    still_size=None,
    setup_overlay=False,
    setup_box=None,
):
    """
    Starts the libcamera -> ffmpeg pipeline and returns two Popen objects:
      p1: camera process (rpicam-vid or libcamera-vid)
      p2: ffmpeg process

    Args:
        ffmpeg_url: RTMP URL for streaming
        width: Landscape capture width in pixels
        height: Landscape capture height in pixels
        rotation: Rotation angle (0, 90, 180, 270 degrees clockwise).
            For 90/270 the streamed output is height x width (portrait).
        framerate: Frame rate in fps
        timestamp_overlay: Whether to show timestamp on video
        sensor_mode: Optional "WIDTH:HEIGHT" string forcing a specific
            sensor mode. Some sensors (e.g. imx708) auto-select a
            center-cropped mode for small outputs, losing field of view;
            forcing the full-FOV binned mode avoids that.
        pixelate_blocks: Optional number of blocks along the streamed
            frame's long side (e.g. 32 gives 32x18 at 16:9). Each block
            is one solid colour, so only coarse shapes and movement show.
            The timestamp is drawn afterwards and stays sharp.
        bitrate: Optional bit rate (bit/s) for the camera's H.264 encoder.
            Defaults to 1 Mbit/s, the value every picam used before this.
        codec: "h264" (camera encodes) or "yuv420" (raw frames, ffmpeg
            does the only encode). See CAMERA_CODEC above.
        x264_preset: libx264 preset whenever ffmpeg encodes.
        max_bitrate: Optional cap (bit/s) on ffmpeg's encode, with a 2 s
            buffer. None leaves it uncapped.
        camera_source: "rpicam-vid", or "picamera2" for picam_source.py,
            which also serves stills on 127.0.0.1:still_port. See
            CAMERA_SOURCE above.
        still_port: Port for those stills.
        still_size: Optional "WIDTHxHEIGHT" for the stills.
        setup_overlay: Centre cross and live focus score on the stream.
        setup_box: Optional (width, height), fractions of the picture: a
            centred box drawn with the setup overlay. See SETUP_BOX above.
    """
    # Get the available camera command
    camera_cmd = get_camera_command()

    # The camera always captures landscape width x height frames, which use
    # the sensor's full field of view. For 90/270 rotation, ffmpeg's
    # transpose filter then turns those frames into height x width
    # (portrait) output. Requesting portrait dimensions from the camera
    # instead would make libcamera crop the sensor to a vertical strip,
    # losing most of the field of view (see ac-dev-lab PR #539).
    cam_width, cam_height = width, height

    # First: camera command with core parameters
    libcamera_cmd = [
        camera_cmd,
        "--inline",
        "--nopreview",
        # Hand each frame to ffmpeg as soon as it is encoded. Without this,
        # stdout to a pipe is block-buffered (4 KB): at 240p and 2 fps that
        # is ~6 frames, which reach ffmpeg together and share one overlay time.
        "--flush",
        "-t",
        "0",
        "--width",
        str(cam_width),  # Scale width
        "--height",
        str(cam_height),  # Scale height
        "--framerate",
        str(framerate),  # Frame rate
        "--codec",
        codec,  # "h264" (camera encodes) or "yuv420" (raw frames)
    ]
    output_target = "-"
    if codec == "h264":
        libcamera_cmd.extend(
            ["--bitrate", str(bitrate or 1000000)]  # ~1 Mbps unless BITRATE is set
        )
        if not os.path.exists("/dev/video11"):
            # No hardware H.264 encoder (Pi 5): rpicam-vid uses libav, which
            # needs the container named and does not understand "-".
            libcamera_cmd.extend(["--libav-format", "h264"])
            output_target = "pipe:1"

    # Force a specific sensor mode if configured (see docstring)
    if sensor_mode:
        libcamera_cmd.extend(["--mode", sensor_mode])

    # Add flip parameters if needed
    if CAMERA_VFLIP:
        libcamera_cmd.extend(["--vflip"])
    if CAMERA_HFLIP:
        libcamera_cmd.extend(["--hflip"])

    # Add output parameters last
    libcamera_cmd.extend(["-o", output_target])  # Output to stdout (pipe)

    if camera_source == "picamera2":
        # The same raw frames from one picamera2 process, which also serves
        # stills. It runs under the system python3, which has picamera2.
        libcamera_cmd = [
            "/usr/bin/python3",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "picam_source.py"),
            "--size",
            f"{cam_width}x{cam_height}",
            "--framerate",
            str(framerate),
            "--port",
            str(still_port),
        ]
        if sensor_mode:
            libcamera_cmd.extend(["--sensor-mode", sensor_mode])
        if still_size:
            libcamera_cmd.extend(["--still-size", still_size])
        if CAMERA_VFLIP:
            libcamera_cmd.append("--vflip")
        if CAMERA_HFLIP:
            libcamera_cmd.append("--hflip")
        if setup_overlay:
            libcamera_cmd.extend(["--overlay-file", OVERLAY_FILE])

    # Build video filter chain for ffmpeg
    video_filters = []

    # Add rotation filter if needed
    if rotation == 90:
        video_filters.append("transpose=1")  # 90 degrees clockwise
    elif rotation == 180:
        video_filters.append("hflip,vflip")  # 180 degrees
    elif rotation == 270:
        video_filters.append(
            "transpose=2"
        )  # 90 degrees counter-clockwise (270 clockwise)

    # Pixelate after rotating, so the blocks line up with the streamed frame,
    # and before the timestamp, so the timestamp stays sharp. Average down to
    # the block grid, then scale back up with nearest-neighbour. The grid is
    # held as 4:4:4 so each block keeps its own colour; in 4:2:0 the colour
    # would be shared by 2x2 neighbouring blocks.
    if pixelate_blocks:
        if rotation in (90, 270):
            out_width, out_height = height, width
        else:
            out_width, out_height = width, height
        block = max(out_width, out_height) / pixelate_blocks
        grid_width = max(1, round(out_width / block))
        grid_height = max(1, round(out_height / block))
        video_filters.append(
            f"scale={grid_width}:{grid_height}:flags=area,format=yuv444p,"
            f"scale={out_width}:{out_height}:flags=neighbor,format=yuv420p"
        )

    # Add timestamp overlay if enabled
    # Format: YYYY-MM-DD_HH-MM-SS. ffmpeg's localtime evaluates per-frame,
    # so the overlay updates once per second at typical framerates.
    if timestamp_overlay:
        # drawtext filter with white text, black background box, in top-left corner
        # fontsize scales with video height for consistent appearance
        if rotation in (90, 270):
            actual_height = width
        else:
            actual_height = height
        fontsize = max(16, actual_height // 20)
        # Note: In ffmpeg drawtext filter, special characters need escaping:
        # - The format separator after localtime uses \:
        # - Colons in the time display (H:M:S) also need escaping
        # - Using dashes instead of colons in time to avoid complex escaping issues
        timestamp_filter = (
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            f":fontsize={fontsize}"
            f":fontcolor=white"
            f":box=1:boxcolor=black@0.5:boxborderw=5"
            f":x=10:y=10"
            f":text='%{{localtime\\:%Y-%m-%d_%H-%M-%S}}'"
        )
        video_filters.append(timestamp_filter)

    # Setup aids: a thin cross through the middle of the frame, to line the
    # deck up on, and the focus score picam_source.py writes once a frame,
    # under the timestamp. drawtext rereads the file for every frame.
    if setup_overlay and camera_source == "picamera2":
        fontsize = max(16, (width if rotation in (90, 270) else height) // 20)
        with open(OVERLAY_FILE, "w") as f:
            f.write("focus ...")
        video_filters.extend(
            [
                "drawbox=x=0:y=ih/2-1:w=iw:h=3:color=orange@0.8:t=fill",
                "drawbox=x=iw/2-1:y=0:w=3:h=ih:color=orange@0.8:t=fill",
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                f":fontsize={fontsize}"
                f":fontcolor=white"
                f":box=1:boxcolor=black@0.5:boxborderw=5"
                f":x=10:y={30 + fontsize}"
                f":textfile={OVERLAY_FILE}:reload=1",
            ]
        )
        if setup_box:
            bw, bh = setup_box
            video_filters.append(
                f"drawbox=x=iw*{(1 - bw) / 2:.5f}:y=ih*{(1 - bh) / 2:.5f}"
                f":w=iw*{bw:.5f}:h=ih*{bh:.5f}:color=orange@0.8:t=3"
            )

    # Second: ffmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        # Generate silent audio source
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=44100",
        # Handle timestamps/threading
        "-thread_queue_size",
        "1024",
        "-use_wallclock_as_timestamps",
        "1",
        # Decode each frame as it arrives. Frame-threaded decoding holds back
        # several frames, which at low frame rates delays the overlay by seconds.
        "-flags",
        "low_delay",
    ]
    if codec == "yuv420":
        # Raw frames: tell ffmpeg their layout, since a pipe has no header.
        # rpicam-vid pads each row to a multiple of 128 pixels (measured on
        # the Pi 5: 1536 arrives as 1536, 2880 as 2944, with zeros on the
        # right), so read the padded width and crop the padding off first.
        stride_width = -(-cam_width // 128) * 128
        if camera_source == "picamera2":
            stride_width = cam_width  # picam_source.py removes the padding
        # The frames are full-range sYCC (BT.601 matrix, levels 0-255), as
        # libcamera reports ("YUV420/sYCC"). Players take untagged HD video as
        # limited-range BT.709, so convert first, or shadows and highlights clip.
        raw_filters = [
            "scale=in_range=pc:out_range=tv"
            ":in_color_matrix=bt601:out_color_matrix=bt709"
        ]
        if stride_width != cam_width:
            raw_filters.insert(0, f"crop={cam_width}:{cam_height}:0:0")
        video_filters[:0] = raw_filters
        ffmpeg_cmd.extend(
            [
                "-f",
                "rawvideo",
                "-pix_fmt",
                "yuv420p",
                "-video_size",
                f"{stride_width}x{cam_height}",
                "-framerate",
                str(framerate),
            ]
        )
    # Read the video from the pipe
    ffmpeg_cmd.extend(["-i", "pipe:0"])

    # Add video filter and encoding settings
    # Note: When filters are applied, libx264 encoding is required which increases
    # CPU usage compared to the original H.264 passthrough. This is unavoidable
    # since ffmpeg cannot apply filters without re-encoding the video stream.
    if video_filters or codec == "yuv420":
        filter_chain = ",".join(video_filters) or "null"
        # YouTube requires a keyframe at least every 4 seconds; libx264's
        # default GOP (250 frames) is far too long at low frame rates, so
        # force a keyframe every 2 seconds.
        ffmpeg_cmd.extend(
            [
                "-vf",
                filter_chain,
                "-c:v",
                "libx264",
                "-preset",
                x264_preset,
                # ffmpeg guesses the input frame rate from the pipe, and at
                # low rates the guess is off (1.5 fps for a 2 fps camera),
                # so pin the output to the camera's rate.
                "-r",
                str(framerate),
                "-g",
                str(framerate * 2),
            ]
        )
        if max_bitrate:
            ffmpeg_cmd.extend(
                ["-maxrate", str(max_bitrate), "-bufsize", str(2 * max_bitrate)]
            )
        if codec == "yuv420":
            # Tag what the scale filter above produced.
            ffmpeg_cmd.extend(
                [
                    "-colorspace",
                    "bt709",
                    "-color_primaries",
                    "bt709",
                    "-color_trc",
                    "bt709",
                    "-color_range",
                    "tv",
                ]
            )
    else:
        ffmpeg_cmd.extend(["-c:v", "copy"])

    ffmpeg_cmd.extend(
        [
            # Encode audio as AAC
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-strict",
            "experimental",
            # Fix non-monotonous DTS warnings by enabling audio synchronization
            # and constant frame rate video output
            "-async",
            "1",
            "-vsync",
            "cfr",
            # Output format is FLV, then final RTMP URL
            "-f",
            "flv",
            ffmpeg_url,
        ]
    )

    # Start camera process, capturing its output in a pipe. Its log goes to
    # our stderr (the journal), not into the pipe: there, libcamera's ~2 KB of
    # start-up log would sit ahead of the first raw frame and shift every frame.
    p1 = subprocess.Popen(libcamera_cmd, stdout=subprocess.PIPE)

    # Start ffmpeg, reading from p1's stdout
    p2 = subprocess.Popen(ffmpeg_cmd, stdin=p1.stdout, stderr=subprocess.STDOUT)

    # Close p1's stdout in the parent process
    p1.stdout.close()

    return p1, p2


def call_lambda(action, CAM_NAME, WORKFLOW_NAME, privacy_status="private"):
    payload = {
        "action": action,
        "cam_name": CAM_NAME,
        "workflow_name": WORKFLOW_NAME,
        "privacy_status": privacy_status,
    }
    print(f"Sending to Lambda: {payload}")
    try:

        response = requests.post(LAMBDA_FUNCTION_URL, json=payload)
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        response.raise_for_status()
        # Try to decode JSON, otherwise fall back to raw text
        try:
            result = response.json()
            if isinstance(result, dict) and "statusCode" in result and "body" in result:
                body = result["body"]
            else:
                body = result
        except ValueError:
            body = response.text

        print(f"Lambda '{action}' succeeded: {body}")
        return body

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error occurred: {e} - Response: {response.text}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to decode Lambda response: {e}")


def end_previous_broadcast():
    try:
        call_lambda("end", CAM_NAME, WORKFLOW_NAME)
    except RuntimeError as e:
        print(f"Could not end previous broadcast; continuing to create a new one: {e}")


if __name__ == "__main__":
    # Validate and get resolution: a preset, or "WIDTHxHEIGHT" for anything
    # else, e.g. "1440x1080" to keep a 4:3 sensor's whole field of view. The
    # 16:9 presets make libcamera crop a 4:3 sensor to 16:9, which on the OT-2
    # lid camera cuts off the front and back rows of deck slots.
    if RESOLUTION in RESOLUTION_MAP:
        width, height = RESOLUTION_MAP[RESOLUTION]
    elif re.fullmatch(r"\d+x\d+", str(RESOLUTION)):
        width, height = (int(v) for v in RESOLUTION.split("x"))
        if width % 2 or height % 2 or width < 64 or height < 64:
            raise ValueError(
                f"Invalid RESOLUTION '{RESOLUTION}'. "
                f"Width and height must be even numbers of at least 64"
            )
    else:
        raise ValueError(
            f"Invalid RESOLUTION '{RESOLUTION}'. "
            f"Allowed options: {list(RESOLUTION_MAP.keys())} or 'WIDTHxHEIGHT'"
        )

    # Validate rotation
    if CAMERA_ROTATION not in (0, 90, 180, 270):
        raise ValueError(
            f"Invalid CAMERA_ROTATION '{CAMERA_ROTATION}'. "
            f"Allowed options: 0, 90, 180, 270"
        )

    # Validate frame rate
    if not isinstance(FRAME_RATE, int) or FRAME_RATE <= 0:
        raise ValueError(
            f"Invalid FRAME_RATE '{FRAME_RATE}'. "
            f"Must be a positive integer (e.g., 15, 24, 30)"
        )

    # Validate codec
    if CAMERA_CODEC not in ("h264", "yuv420"):
        raise ValueError(
            f"Invalid CAMERA_CODEC '{CAMERA_CODEC}'. Allowed options: h264, yuv420"
        )

    # Validate the camera source
    if CAMERA_SOURCE not in ("rpicam-vid", "picamera2"):
        raise ValueError(
            f"Invalid CAMERA_SOURCE '{CAMERA_SOURCE}'. "
            f"Allowed options: rpicam-vid, picamera2"
        )
    if CAMERA_SOURCE == "picamera2" and CAMERA_CODEC != "yuv420":
        raise ValueError('CAMERA_SOURCE = "picamera2" needs CAMERA_CODEC = "yuv420"')

    # Validate pixelation
    if PIXELATE_BLOCKS is not None and (
        not isinstance(PIXELATE_BLOCKS, int) or PIXELATE_BLOCKS < 0
    ):
        raise ValueError(
            f"Invalid PIXELATE_BLOCKS '{PIXELATE_BLOCKS}'. "
            f"Must be a positive integer (e.g., 32), or 0 or None for none"
        )

    # Validate the encoder cap
    if MAX_BITRATE is not None and (
        not isinstance(MAX_BITRATE, int) or MAX_BITRATE <= 0
    ):
        raise ValueError(
            f"Invalid MAX_BITRATE '{MAX_BITRATE}'. "
            f"Must be a positive integer in bit/s (e.g., 4000000), or None"
        )

    # For 90/270 rotation, output is portrait (swapped dimensions)
    if CAMERA_ROTATION in (90, 270):
        output_width, output_height = height, width
        orientation = "portrait"
    else:
        output_width, output_height = width, height
        orientation = "landscape"

    print(
        f"Using resolution: {RESOLUTION} ({output_width}x{output_height} {orientation})"
    )
    print(f"Using rotation: {CAMERA_ROTATION} degrees")
    print(f"Using frame rate: {FRAME_RATE} fps")
    print(f"Sensor mode: {SENSOR_MODE or 'auto'}")
    print(f"Camera codec: {CAMERA_CODEC}")
    print(f"Camera source: {CAMERA_SOURCE}")
    if CAMERA_SOURCE == "picamera2":
        print(f"Stills: 127.0.0.1:{STILL_PORT}/still, {STILL_SIZE or 'sensor mode size'}")
        print(f"Setup overlay: {'on' if SETUP_OVERLAY else 'off'}, box: {SETUP_BOX or 'none'}")
    print(f"Camera bitrate: {BITRATE or 1000000} bit/s")
    print(f"x264 preset: {X264_PRESET}, cap: {MAX_BITRATE or 'none'} bit/s")
    print(f"Timestamp overlay: {'enabled' if TIMESTAMP_OVERLAY else 'disabled'}")
    if PIXELATE_BLOCKS:
        print(f"Pixelation: {PIXELATE_BLOCKS} blocks along the long side")
    else:
        print("Pixelation: off")

    # End previous broadcast and start a new one via Lambda
    end_previous_broadcast()
    raw_body = call_lambda(
        "create", CAM_NAME, WORKFLOW_NAME, privacy_status=PRIVACY_STATUS
    )
    try:
        result = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        ffmpeg_url = result["result"]["ffmpeg_url"]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise RuntimeError(
            f"Cannot proceed: ffmpeg_url not found or response invalid → {e}"
        )

    print(f"Streaming to: {ffmpeg_url}")

    while True:
        print("Starting stream..")
        p1, p2 = start_stream(
            ffmpeg_url,
            width,
            height,
            CAMERA_ROTATION,
            FRAME_RATE,
            TIMESTAMP_OVERLAY,
            sensor_mode=SENSOR_MODE,
            pixelate_blocks=PIXELATE_BLOCKS,
            bitrate=BITRATE,
            codec=CAMERA_CODEC,
            x264_preset=X264_PRESET,
            max_bitrate=MAX_BITRATE,
            camera_source=CAMERA_SOURCE,
            still_port=STILL_PORT,
            still_size=STILL_SIZE,
            setup_overlay=SETUP_OVERLAY,
            setup_box=SETUP_BOX,
        )
        print("Stream started")
        interrupted = False
        try:
            p2.wait()
        except KeyboardInterrupt:
            print("Received interrupt signal, exiting...")
            interrupted = True
        except Exception as e:
            print(e)
        finally:
            print("Terminating processes..")
            p1.terminate()
            p2.terminate()
            # Let the camera process exit, and so release the camera, before
            # the next start tries to open it.
            try:
                p1.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p1.kill()
                p1.wait()
            print("Processes terminated.")
            if interrupted:
                break
            else:
                print("Retrying..")
