#!/usr/bin/env python3
"""Generate animated wobbly sunny side up eggs sprite using Gemini Veo API."""

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


def extract_frames(video_path, output_dir, num_frames=8):
    """Extract evenly-spaced frames from video."""
    # Get video duration first
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
        f"{output_dir}/egg_frame_%d.png"
    ]
    subprocess.run(cmd, capture_output=True)


def main():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = (
        "Two sunny side up fried eggs flying through the air, wobbling and jiggling "
        "like jello in a smooth repeating animation cycle, the egg whites wobble "
        "and the yellow yolks bounce slightly, pixel art style, 32-bit retro game "
        "aesthetic, bright solid green chroma key background (#00FF00), "
        "the eggs stay centered in frame while wobbling, side view, "
        "classic 1990s video game sprite style, no text, no labels"
    )

    print("Generating wobbly eggs video with Veo...")
    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="16:9",
            number_of_videos=1,
            duration_seconds=4,
        ),
    )

    # Poll for completion
    print("Waiting for video generation (this takes 1-2 minutes)...")
    while not operation.done:
        time.sleep(10)
        operation = client.operations.get(operation)
        print(".", end="", flush=True)
    print(" Done!")

    sprites_dir = Path(__file__).parent / "sprites"
    sprites_dir.mkdir(exist_ok=True)

    video_path = sprites_dir / "eggs_video.mp4"

    # Download the result
    result = operation.result
    video = result.generated_videos[0]
    client.files.download(file=video.video)
    video.video.save(str(video_path))
    print(f"Saved video to {video_path}")

    # Extract frames
    print("Extracting frames...")
    extract_frames(video_path, sprites_dir, num_frames=8)

    # Remove green screen from each frame
    print("Removing green backgrounds...")
    for i in range(1, 20):  # ffmpeg starts at 1
        raw_path = sprites_dir / f"egg_frame_{i}.png"
        if raw_path.exists():
            final_path = sprites_dir / f"egg_frame_{i-1}.png"
            remove_green_screen(raw_path, final_path)
            if i > 1:  # Don't delete the first one yet
                raw_path.unlink()
            print(f"  Processed frame {i-1}")

    # Clean up frame 1 raw (now egg_frame_0.png exists)
    raw_first = sprites_dir / "egg_frame_1.png"
    if raw_first.exists():
        raw_first.unlink()

    print("Done!")


if __name__ == "__main__":
    main()
