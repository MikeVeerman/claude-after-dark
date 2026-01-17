# Claude Code Prompt: Generate Flying Toasters Sprites

Copy and paste the prompt below into Claude Code to generate animated flying toaster sprites in the style of the classic After Dark screensaver.

---

## The Prompt

```
I want to recreate the classic "Flying Toasters" screensaver from After Dark.

Generate animated sprite frames for a flying toaster with angel wings:
- 8 frames showing wings flapping up and down in a smooth cycle
- Consistent toaster design across all frames
- Transparent background for compositing
- Pixel art style, 32-bit retro game aesthetic
- Chrome silver toaster with white feathered angel wings
- Side view profile

Use Google's Gemini API. My API key is in the GEMINI_API_KEY environment variable.

Approach:
1. Use Veo 3.1 video generation to create a 4-second video of the toaster flying with flapping wings
2. Request a green screen background for chroma keying
3. Extract 8 frames from the video using ffmpeg
4. Remove the green background with PIL to create transparent PNGs
5. Save as toaster_frame_0.png through toaster_frame_7.png in a sprites/ directory

After generating, show me the frames so I can verify the wing positions vary and the design is consistent.
```

---

## How It Works

When you give Claude Code this prompt, it will:

1. **Write a Python script** that calls Gemini Veo 3.1 to generate a video
2. **Generate a 4-second video** of a flying toaster on green background
3. **Extract 8 frames** using ffmpeg (one every 0.5 seconds)
4. **Remove green pixels** and replace with transparency using PIL
5. **Show you the frames** so you can give feedback

### Giving Feedback

After seeing the results, tell Claude what to fix:

- "The green background wasn't fully removed" → Claude fixes the chroma key algorithm
- "The wings don't move enough between frames" → Claude adjusts the prompt
- "The toaster looks different in some frames" → Claude regenerates
- "I also need a toast sprite with transparent background" → Claude generates it

---

## Prerequisites

1. **Gemini API Key**: Get one from https://aistudio.google.com/
2. **Set environment variable**: `export GEMINI_API_KEY="your-key-here"`
3. **FFmpeg**: `sudo apt install ffmpeg` (Linux) or `brew install ffmpeg` (Mac)
4. **Python packages**: `pip install google-genai pillow`

---

## What Gets Generated

```
sprites/
├── toaster_frame_0.png   # Wings up
├── toaster_frame_1.png   # Wings mid-up
├── toaster_frame_2.png   # Wings horizontal
├── toaster_frame_3.png   # Wings mid-down
├── toaster_frame_4.png   # Wings down
├── toaster_frame_5.png   # Wings mid-down
├── toaster_frame_6.png   # Wings horizontal
├── toaster_frame_7.png   # Wings mid-up
└── toaster_video.mp4     # Source video
```

All PNGs have transparent backgrounds, ready for use in pygame, godot, or any game engine.

---

## Follow-up Prompts

After the toaster sprites are done:

**Add toast sprite:**
```
Now generate a single toast sprite (not animated) with transparent background.
Pixel art style matching the toaster. Remove any black background.
```

**Create the screensaver:**
```
Write a pygame screensaver that:
- Loads all toaster frames from sprites/
- Spawns toasters flying diagonally across a black screen
- Animates the wing flapping by cycling through frames
- Exits on mouse movement or keypress
- Runs fullscreen
```

**Adjust animation speed:**
```
The wings flap too fast. Increase the frame delay in the animation code.
```

---

## Quick Start

```bash
# 1. Set your API key
export GEMINI_API_KEY="your-key-here"

# 2. Open Claude Code
claude

# 3. Paste the prompt above

# 4. Wait for generation (~2 minutes for video)

# 5. Review the frames Claude shows you

# 6. Give feedback or say "commit it" when satisfied
```
