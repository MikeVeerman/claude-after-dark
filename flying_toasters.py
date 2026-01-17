#!/usr/bin/env python3
"""
Flying Toasters Screensaver - After Dark style
Using Gemini-generated pixel art sprites
"""

import random
import pygame
import sys
from pathlib import Path


# Colors
BLACK = (0, 0, 0)

# Sprite size (scale down from 1024x1024)
TOASTER_SIZE = 128
TOAST_SIZE = 80
BAGUETTE_SIZE = 100
EGG_SIZE = 120


def load_sprites(sprites_dir: Path):
    """Load and scale sprite images"""
    toaster_frames = []

    # Load toaster frames - dynamically find all available frames
    i = 0
    while True:
        path = sprites_dir / f"toaster_frame_{i}.png"
        if path.exists():
            img = pygame.image.load(str(path)).convert_alpha()
            img = pygame.transform.smoothscale(img, (TOASTER_SIZE, TOASTER_SIZE))
            toaster_frames.append(img)
            i += 1
        else:
            break

    # If we have few frames (3 or less), add reverse frames for ping-pong animation
    # This creates smooth wing cycles: up -> mid -> down -> mid -> up...
    if 2 <= len(toaster_frames) <= 4:
        # Add frames in reverse (excluding first and last) for smooth loop
        toaster_frames.extend(toaster_frames[-2:0:-1])

    # Load toast
    toast_path = sprites_dir / "toast.png"
    toast_frames = []
    if toast_path.exists():
        img = pygame.image.load(str(toast_path)).convert_alpha()
        img = pygame.transform.smoothscale(img, (TOAST_SIZE, TOAST_SIZE))
        toast_frames.append(img)

    # Load baguette
    baguette_path = sprites_dir / "baguette.png"
    baguette_frames = []
    if baguette_path.exists():
        img = pygame.image.load(str(baguette_path)).convert_alpha()
        img = pygame.transform.smoothscale(img, (BAGUETTE_SIZE, BAGUETTE_SIZE))
        baguette_frames.append(img)

    # Load egg frames (animated)
    egg_frames = []
    i = 0
    while True:
        path = sprites_dir / f"egg_frame_{i}.png"
        if path.exists():
            img = pygame.image.load(str(path)).convert_alpha()
            img = pygame.transform.smoothscale(img, (EGG_SIZE, EGG_SIZE))
            egg_frames.append(img)
            i += 1
        else:
            break

    # Ping-pong for smooth wobble loop
    if 2 <= len(egg_frames) <= 8:
        egg_frames.extend(egg_frames[-2:0:-1])

    return toaster_frames, toast_frames, baguette_frames, egg_frames


class FlyingSprite:
    """A sprite that flies across the screen"""

    def __init__(self, frames, x, y, speed_x, speed_y, frame_delay=8):
        self.frames = frames
        self.x = float(x)
        self.y = float(y)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.frame_index = random.randint(0, len(frames) - 1)
        self.frame_delay = frame_delay
        self.frame_counter = 0
        self.width = frames[0].get_width()
        self.height = frames[0].get_height()

    def update(self):
        """Update sprite position and animation frame"""
        self.x += self.speed_x
        self.y += self.speed_y

        # Cycle through animation frames
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, screen):
        """Draw the sprite"""
        screen.blit(self.frames[self.frame_index], (int(self.x), int(self.y)))

    def is_off_screen(self, screen_width, screen_height):
        """Check if sprite has flown off screen"""
        return (self.x + self.width < 0) or (self.y > screen_height)


def main():
    pygame.init()

    # Get display info for fullscreen
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h

    # Create fullscreen window
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Flying Toasters")
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()

    # Load sprites
    sprites_dir = Path(__file__).parent / "sprites"
    toaster_frames, toast_frames, baguette_frames, egg_frames = load_sprites(sprites_dir)

    if not toaster_frames:
        print("Error: No toaster sprites found. Run generate_sprites.py first.")
        pygame.quit()
        sys.exit(1)

    sprites = []
    spawn_timer = 0
    spawn_interval = 30  # Frames between spawns

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                # Exit on significant mouse movement
                if abs(event.rel[0]) > 5 or abs(event.rel[1]) > 5:
                    running = False

        # Spawn new sprites
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            if len(sprites) < 20:
                # Random spawn position
                if random.random() < 0.7:
                    x = screen_width + 10
                    y = random.randint(-100, screen_height // 2)
                else:
                    x = random.randint(screen_width // 2, screen_width + 10)
                    y = -100

                # Random speed
                speed_x = random.uniform(-4, -2)
                speed_y = random.uniform(1, 2.5)

                # 50% toasters, 15% toast, 15% baguettes, 20% eggs
                roll = random.random()
                if roll < 0.5:
                    sprite = FlyingSprite(toaster_frames, x, y, speed_x, speed_y,
                                         frame_delay=random.randint(6, 10))
                elif roll < 0.65 and toast_frames:
                    sprite = FlyingSprite(toast_frames, x, y, speed_x, speed_y)
                elif roll < 0.80 and baguette_frames:
                    sprite = FlyingSprite(baguette_frames, x, y, speed_x, speed_y)
                elif egg_frames:
                    sprite = FlyingSprite(egg_frames, x, y, speed_x, speed_y,
                                         frame_delay=random.randint(8, 12))
                else:
                    sprite = FlyingSprite(toaster_frames, x, y, speed_x, speed_y,
                                         frame_delay=random.randint(6, 10))

                sprites.append(sprite)

        # Update sprites
        for sprite in sprites[:]:
            sprite.update()
            if sprite.is_off_screen(screen_width, screen_height):
                sprites.remove(sprite)

        # Draw
        screen.fill(BLACK)
        for sprite in sprites:
            sprite.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
