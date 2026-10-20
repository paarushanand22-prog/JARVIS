"""
Apple-Style Cinematic Commercial Video Generator for J.A.R.V.I.S.
Creates a 1080p 60FPS cinematic keynote product film with clean typography,
smooth ease-in-out animations, dark titanium minimalism, voiceover narrative,
and audio muxing via FFmpeg.
"""

import os
import cv2
import math
import asyncio
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import imageio_ffmpeg

WIDTH, HEIGHT = 1920, 1080
FPS = 60
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
OUTPUT_VIDEO = os.path.join(DESKTOP_DIR, "JARVIS_Apple_Keynote_Commercial.mp4")
TEMP_VIDEO = os.path.join(DESKTOP_DIR, "temp_video.mp4")
TEMP_AUDIO = os.path.join(DESKTOP_DIR, "temp_voiceover.mp3")

# Apple-Style Titanium Palette
BG_BLACK = (5, 5, 7)
TEXT_WHITE = (245, 245, 247)
TEXT_MUTED = (134, 134, 139)
TEXT_CYAN = (41, 151, 255) # Apple Blue
ACCENT_GREEN = (48, 209, 88)
CARD_BG = (22, 22, 24)
CARD_BORDER = (45, 45, 48)

# Load fonts
try:
    FONT_HERO = ImageFont.truetype("segoeuib.ttf", 95)
    FONT_TITLE = ImageFont.truetype("segoeuib.ttf", 64)
    FONT_SUBTITLE = ImageFont.truetype("segoeui.ttf", 36)
    FONT_BODY = ImageFont.truetype("segoeui.ttf", 28)
    FONT_BADGE = ImageFont.truetype("segoeuib.ttf", 22)
    FONT_PRICE = ImageFont.truetype("segoeuib.ttf", 85)
except Exception:
    FONT_HERO = FONT_TITLE = FONT_SUBTITLE = FONT_BODY = FONT_BADGE = FONT_PRICE = ImageFont.load_default()

def ease_out_cubic(x):
    return 1 - pow(1 - x, 3)

def ease_in_out(x):
    return -(math.cos(math.pi * x) - 1) / 2

# Cinematic Voiceover Script
VOICEOVER_TEXT = (
    "Meet JARVIS. The next generation autonomous AI workstation for Windows. "
    "Designed with total privacy, zero cloud leaks, and pure local intelligence. "
    "Control your entire PC by voice or typed commands. "
    "Analyze any active screen in real-time with sub-fifty-millisecond vision. "
    "Automate complex PowerPoint presentations and desktop workflows on command. "
    "Experience the future of personal computing. Just five dollars a month. "
    "JARVIS. Intelligence, redefined."
)

async def generate_voiceover():
    print("[1/3] Synthesizing Apple-style Indian English Voiceover...")
    communicate = edge_tts.Communicate(VOICEOVER_TEXT, "en-IN-PrabhatNeural", rate="-2%", pitch="+0Hz")
    await communicate.save(TEMP_AUDIO)
    print(" Voiceover audio generated successfully.")

def draw_apple_pill(draw, text, cx, cy):
    bbox = draw.textbbox((0, 0), text, font=FONT_BADGE)
    w = bbox[2] - bbox[0] + 36
    h = bbox[3] - bbox[1] + 16
    x1, y1 = cx - w//2, cy - h//2
    x2, y2 = cx + w//2, cy + h//2
    draw.rounded_rectangle([x1, y1, x2, y2], radius=18, fill=(28, 28, 30), outline=(60, 60, 65), width=1)
    draw.text((cx - (bbox[2]-bbox[0])//2, y1 + 6), text, font=FONT_BADGE, fill=TEXT_CYAN)

def draw_glowing_core(draw, cx, cy, radius, t):
    pulse = math.sin(t * 3.0) * 8
    r = radius + pulse
    # Concentric rings
    for i in range(3):
        cur_r = r + i * 25
        alpha = int(255 * (1.0 - (i / 3.0)))
        draw.ellipse([cx - cur_r, cy - cur_r, cx + cur_r, cy + cur_r], outline=(30, 90, 180), width=2)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(41, 151, 255), width=4)
    draw.ellipse([cx - r*0.4, cy - r*0.4, cx + r*0.4, cy + r*0.4], fill=(245, 245, 247))

def render_scenes():
    print("[2/3] Rendering 1080p 60FPS Apple-Style Motion Graphics...")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(TEMP_VIDEO, fourcc, FPS, (WIDTH, HEIGHT))

    # Total duration ~26 seconds = 1560 frames
    total_frames = 1560

    scenes = [
        # (name, start_frame, duration)
        ("INTRO", 0, 240),            # 0-4s: Silence, glow core, "Meet JARVIS."
        ("LOCAL_AI", 240, 300),        # 4-9s: "Local Intelligence. Zero Cloud Leaks."
        ("VISION", 540, 300),          # 9-14s: "Live Screen Vision. Sub-50ms."
        ("AUTONOMY", 840, 300),        # 14-19s: "Autonomous Device Orders & PowerPoint."
        ("PRICING", 1140, 240),        # 19-23s: "$5 / month. Instant Activation."
        ("OUTRO", 1380, 180)           # 23-26s: "JARVIS. Available Now."
    ]

    for frame_idx in range(total_frames):
        img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_BLACK)
        draw = ImageDraw.Draw(img)
        t = frame_idx / FPS

        # --- Scene 1: INTRO (0 - 4s) ---
        if frame_idx < 240:
            prog = min(1.0, frame_idx / 90.0)
            fade = ease_out_cubic(prog)
            draw_apple_pill(draw, "AUTONOMOUS DESKTOP INTELLIGENCE", WIDTH//2, 280)
            draw_glowing_core(draw, WIDTH//2, HEIGHT//2 - 20, 70, t)

            title_text = "Meet J.A.R.V.I.S."
            bbox = draw.textbbox((0, 0), title_text, font=FONT_HERO)
            tw = bbox[2] - bbox[0]
            draw.text((WIDTH//2 - tw//2, HEIGHT//2 + 130), title_text, font=FONT_HERO, fill=TEXT_WHITE)

            sub_text = "The personal AI executive workstation for Windows."
            sbox = draw.textbbox((0, 0), sub_text, font=FONT_SUBTITLE)
            sw = sbox[2] - sbox[0]
            draw.text((WIDTH//2 - sw//2, HEIGHT//2 + 250), sub_text, font=FONT_SUBTITLE, fill=TEXT_MUTED)

        # --- Scene 2: LOCAL AI (4 - 9s) ---
        elif frame_idx < 540:
            rel = (frame_idx - 240) / 300.0
            draw_apple_pill(draw, "100% PRIVATE • ZERO SUBSCRIPTION LOCK-IN", WIDTH//2, 240)

            title_text = "Local Power. Zero Leaks."
            bbox = draw.textbbox((0, 0), title_text, font=FONT_TITLE)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, 300), title_text, font=FONT_TITLE, fill=TEXT_WHITE)

            # Three minimalist metric cards
            card_w, card_h = 420, 260
            coords = [(260, 440), (750, 440), (1240, 440)]
            specs = [
                ("100% Offline", "Runs strictly on your GPU.\nNo telemetry or cloud logs."),
                ("< 50ms OCR", "Sub-frame vision processing.\nInstant reading of any window."),
                ("Native Audio", "English (India) neural synthesis.\nClear, natural dialog.")
            ]

            for i, (cx, cy) in enumerate(coords):
                card_rel = max(0.0, min(1.0, (rel - i * 0.15) / 0.4))
                card_fade = ease_out_cubic(card_rel)
                y_offset = int((1.0 - card_fade) * 40)
                draw.rounded_rectangle([cx, cy + y_offset, cx + card_w, cy + card_h + y_offset], radius=20, fill=CARD_BG, outline=CARD_BORDER, width=1)
                
                h_text, b_text = specs[i]
                draw.text((cx + 36, cy + 36 + y_offset), h_text, font=FONT_SUBTITLE, fill=TEXT_CYAN)
                draw.text((cx + 36, cy + 110 + y_offset), b_text, font=FONT_BODY, fill=TEXT_MUTED)

        # --- Scene 3: LIVE SCREEN VISION (9 - 14s) ---
        elif frame_idx < 840:
            draw_apple_pill(draw, "REAL-TIME MULTIMODAL SENSING", WIDTH//2, 220)

            title_text = "It sees what you see."
            bbox = draw.textbbox((0, 0), title_text, font=FONT_TITLE)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, 280), title_text, font=FONT_TITLE, fill=TEXT_WHITE)

            # Modern Glass Terminal Window Mockup
            tx1, ty1, tx2, ty2 = 360, 390, WIDTH - 360, 860
            draw.rounded_rectangle([tx1, ty1, tx2, ty2], radius=24, fill=(14, 14, 16), outline=(45, 45, 50), width=1)
            # Terminal title bar
            draw.rounded_rectangle([tx1, ty1, tx2, ty1 + 55], radius=24, fill=(24, 24, 28))
            draw.rectangle([tx1, ty1 + 35, tx2, ty1 + 55], fill=(24, 24, 28))
            # Mac / Apple style dots
            draw.ellipse([tx1 + 25, ty1 + 20, tx1 + 39, ty1 + 34], fill=(255, 95, 86))
            draw.ellipse([tx1 + 47, ty1 + 20, tx1 + 61, ty1 + 34], fill=(255, 189, 46))
            draw.ellipse([tx1 + 69, ty1 + 20, tx1 + 83, ty1 + 34], fill=(39, 201, 63))

            draw.text((tx1 + 40, ty1 + 85), "User: \"Jarvis, what is currently open on my screen?\"", font=FONT_BODY, fill=TEXT_WHITE)
            draw.text((tx1 + 40, ty1 + 145), "[VISION CORE] Active window inspected in 34ms via RTX acceleration.", font=FONT_BODY, fill=TEXT_CYAN)
            draw.text((tx1 + 40, ty1 + 205), "JARVIS: \"Sir, you have your presentation editor active with 4 slides open,\"", font=FONT_BODY, fill=ACCENT_GREEN)
            draw.text((tx1 + 40, ty1 + 250), "        \"and your browser on the official download page.\"", font=FONT_BODY, fill=ACCENT_GREEN)

        # --- Scene 4: AUTONOMOUS DEVICE ACTIONS (14 - 19s) ---
        elif frame_idx < 1140:
            draw_apple_pill(draw, "COMPLETE HARDWARE & OS CONTROL", WIDTH//2, 220)

            title_text = "Effortless Automation."
            bbox = draw.textbbox((0, 0), title_text, font=FONT_TITLE)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, 280), title_text, font=FONT_TITLE, fill=TEXT_WHITE)

            # Features Showcase Row
            caps = [
                ("PowerPoint Creation", "Author fully structured, formatted slide decks in seconds."),
                ("Targeted Mouse Clicks", "Locates any UI button, menu, or link and clicks autonomously."),
                ("Instant Multi-Drive Search", "Searches 500,000+ files across drives C:, D:, E: in under 1 second.")
            ]
            for idx, (cap_title, cap_desc) in enumerate(caps):
                cy = 400 + idx * 135
                draw.rounded_rectangle([380, cy, WIDTH - 380, cy + 105], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=1)
                draw.text((420, cy + 22), cap_title, font=FONT_SUBTITLE, fill=TEXT_WHITE)
                draw.text((420, cy + 62), cap_desc, font=FONT_BODY, fill=TEXT_MUTED)

        # --- Scene 5: PRICING (19 - 23s) ---
        elif frame_idx < 1380:
            draw_apple_pill(draw, "SIMPLE, TRANSPARENT VALUE", WIDTH//2, 220)

            title_text = "Pro AI. Accessible to everyone."
            bbox = draw.textbbox((0, 0), title_text, font=FONT_TITLE)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, 280), title_text, font=FONT_TITLE, fill=TEXT_WHITE)

            # Centered Minimalist Pricing Card
            cx1, cy1, cx2, cy2 = WIDTH//2 - 280, 390, WIDTH//2 + 280, 830
            draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=28, fill=CARD_BG, outline=TEXT_CYAN, width=2)

            draw.text((cx1 + 45, cy1 + 50), "Commercial Pro", font=FONT_SUBTITLE, fill=TEXT_WHITE)
            draw.text((cx1 + 45, cy1 + 105), "Standalone Windows 10 & 11 Binary", font=FONT_BODY, fill=TEXT_MUTED)

            draw.text((cx1 + 45, cy1 + 175), "$5", font=FONT_PRICE, fill=TEXT_WHITE)
            draw.text((cx1 + 160, cy1 + 225), "/ month", font=FONT_SUBTITLE, fill=TEXT_MUTED)

            features = [
                "✓ Unlimited Hands-Free Voice & Text",
                "✓ Real-Time Screen Vision & Deep OCR",
                "✓ Autonomous PowerPoint Generation",
                "✓ HWID Locked Security & Updates"
            ]
            for fi, feat in enumerate(features):
                draw.text((cx1 + 45, cy1 + 295 + fi * 42), feat, font=FONT_BODY, fill=TEXT_WHITE)

        # --- Scene 6: OUTRO (23 - 26s) ---
        else:
            prog = min(1.0, (frame_idx - 1380) / 60.0)
            fade = ease_out_cubic(prog)

            draw_glowing_core(draw, WIDTH//2, HEIGHT//2 - 90, 80, t)

            title_text = "J.A.R.V.I.S."
            bbox = draw.textbbox((0, 0), title_text, font=FONT_HERO)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, HEIGHT//2 + 40), title_text, font=FONT_HERO, fill=TEXT_WHITE)

            sub_text = "Intelligence, Redefined. Available Now."
            sbox = draw.textbbox((0, 0), sub_text, font=FONT_SUBTITLE)
            draw.text((WIDTH//2 - (sbox[2]-sbox[0])//2, HEIGHT//2 + 165), sub_text, font=FONT_SUBTITLE, fill=TEXT_CYAN)

            cta_text = "Download at the official site • Instant Activation"
            cbox = draw.textbbox((0, 0), cta_text, font=FONT_BODY)
            draw.text((WIDTH//2 - (cbox[2]-cbox[0])//2, HEIGHT//2 + 250), cta_text, font=FONT_BODY, fill=TEXT_MUTED)

        # Convert PIL Image to OpenCV frame (RGB -> BGR)
        cv_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(cv_frame)

    out.release()
    print(" Video stream rendered successfully.")

def mux_audio_and_video():
    print("[3/3] Muxing Voiceover Audio & 60FPS Video with FFmpeg...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", TEMP_VIDEO,
        "-i", TEMP_AUDIO,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_VIDEO
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Cleanup temporary tracks
    if os.path.exists(TEMP_VIDEO):
        os.remove(TEMP_VIDEO)
    if os.path.exists(TEMP_AUDIO):
        os.remove(TEMP_AUDIO)
        
    print(f"\n Master YouTube Video ready at:\n{OUTPUT_VIDEO}\n")

if __name__ == "__main__":
    asyncio.run(generate_voiceover())
    render_scenes()
    mux_audio_and_video()
