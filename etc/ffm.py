import shutil
import subprocess
import sys


def install_ffmpeg():
    try:
        if sys.platform == "win32":
            subprocess.check_call(["choco", "install", "ffmpeg", "-y"])
        else:
            raise EnvironmentError("Unsupported platform. Please install ffmpeg and ffprobe manually.")
        print("ffmpeg and ffprobe installed successfully.")
    except Exception as ex:
        raise EnvironmentError(f"Failed to install ffmpeg and ffprobe: {ex}")


def check_for_ffmpeg():
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")

    if ffmpeg_path and ffprobe_path:
        print(f"ffmpeg found at {ffmpeg_path}")
        print(f"ffprobe found at {ffprobe_path}")
    else:
        missing = []
        if not ffmpeg_path:
            missing.append("ffmpeg")
        if not ffprobe_path:
            missing.append("ffprobe")
        raise EnvironmentError(
            f"Missing dependencies: {', '.join(missing)}. Please install them and ensure they are in your PATH.")
