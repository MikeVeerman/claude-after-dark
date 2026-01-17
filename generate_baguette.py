#!/usr/bin/env python3
"""Generate a baguette sprite using Gemini Imagen API."""

import os
from pathlib import Path
from google import genai
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


def main():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = (
        "A single French baguette bread, pixel art style, 32-bit retro game aesthetic, "
        "golden brown crusty baguette, diagonal orientation flying through the air, "
        "bright solid green chroma key background (#00FF00), "
        "classic 1990s video game sprite style, no text, no labels"
    )

    print("Generating baguette sprite with Imagen...")
    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config={
            "number_of_images": 1,
        }
    )

    sprites_dir = Path(__file__).parent / "sprites"
    sprites_dir.mkdir(exist_ok=True)

    raw_path = sprites_dir / "baguette_raw.png"
    final_path = sprites_dir / "baguette.png"

    # Save raw image
    image = response.generated_images[0]
    image.image.save(str(raw_path))
    print(f"Saved raw image to {raw_path}")

    # Remove green screen
    print("Removing green background...")
    remove_green_screen(raw_path, final_path)
    print(f"Saved final sprite to {final_path}")

    # Clean up raw file
    raw_path.unlink()
    print("Done!")


if __name__ == "__main__":
    main()
