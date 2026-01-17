#!/usr/bin/env python3
"""Generate animated flying toaster sprites with isometric view using Gemini Veo API."""

import os
import subprocess
import time
from pathlib import Path
from google import genai
from google.genai import types
from PIL import Image


def remove_green_screen(image_path, output_path):
    """Remove green-dominant pixels and save with transparency."""
    img = Image.open(image_path).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # Calculate how much greener this pixel is than red/blue
            green_dominance = g - max(r, b)

            # Strong green = fully transparent
            if green_dominance > 20 and g > 100:
                pixels[x, y] = (0, 0, 0, 0)

            # Slight green tint = partial transparency (anti-aliasing)
            elif green_dominance > 5 and g > 80:
                alpha_factor = 1 - (green_dominance / 100)
                new_alpha = int(a * max(0, min(1, alpha_factor)))
                pixels[x, y] = (r, g, b, new_alpha)

    img.save(output_path, "PNG")


def extract_frames(video_path, output_dir, prefix, num_frames=8):
    """Extract evenly-spaced frames from video."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True
    )
    duration = float(result.stdout.strip())
    fps = num_frames / duration

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"fps={fps}",
        f"{output_dir}/{prefix}_%d.png"
    ]
    subprocess.run(cmd, capture_output=True)


def main():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = (
        "A chrome silver retro toaster with white feathered angel wings "
        "flying through the air, wings flapping up and down in a smooth "
        "repeating animation cycle, three-quarter isometric view from "
        "front-left angle showing depth, the toaster flies diagonally "
        "down-left like the classic After Dark screensaver, pixel art style, "
        "32-bit retro game aesthetic, bright solid green chroma key "
        "background (#00FF00), the toaster stays centered in frame while "
        "wings animate, classic 1990s After Dark flying toasters "
        "screensaver style, no text, no labels"
    )

    print("Generating isometric toaster video with Veo...")
    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="16:9",
            number_of_videos=1,
            duration_seconds=4,
        ),
    )

    print("Waiting for video generation (this takes 1-2 minutes)...")
    while not operation.done:
        time.sleep(10)
        operation = client.operations.get(operation)
        print(".", end="", flush=True)
    print(" Done!")

    sprites_dir = Path(__file__).parent / "sprites"
    sprites_dir.mkdir(exist_ok=True)

    # Backup old toaster files
    for old_file in sprites_dir.glob("toaster_frame_*.png"):
        old_file.rename(old_file.with_suffix(".png.bak"))

    video_path = sprites_dir / "toaster_video.mp4"

    # Download the result
    result = operation.result
    video = result.generated_videos[0]
    client.files.download(file=video.video)
    video.video.save(str(video_path))
    print(f"Saved video to {video_path}")

    # Extract frames
    print("Extracting frames...")
    extract_frames(video_path, sprites_dir, "toaster_raw", num_frames=8)

    # Remove green screen from each frame
    print("Removing green backgrounds...")
    frame_count = 0
    for i in range(1, 20):  # ffmpeg starts at 1
        raw_path = sprites_dir / f"toaster_raw_{i}.png"
        if raw_path.exists():
            final_path = sprites_dir / f"toaster_frame_{frame_count}.png"
            remove_green_screen(raw_path, final_path)
            raw_path.unlink()
            print(f"  Processed frame {frame_count}")
            frame_count += 1

    # Remove backups
    for bak_file in sprites_dir.glob("*.png.bak"):
        bak_file.unlink()

    print(f"Done! Generated {frame_count} frames.")


if __name__ == "__main__":
    main()
