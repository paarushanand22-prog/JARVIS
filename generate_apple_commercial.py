"""
Full-Length Apple Keynote Cinematic Product Film for J.A.R.V.I.S.
Total duration: ~65 seconds.
Per-scene synchronized voiceover + motion graphics + cinematic transitions.
1080p 60FPS.
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
TEMP_DIR = os.path.join(DESKTOP_DIR, "jarvis_video_temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Apple Titanium Minimalist Palette
BG_BLACK = (6, 7, 10)
TEXT_WHITE = (245, 245, 247)
TEXT_MUTED = (140, 142, 150)
ACCENT_BLUE = (41, 151, 255)
ACCENT_GREEN = (48, 209, 88)
ACCENT_PURPLE = (191, 90, 242)
ACCENT_ORANGE = (255, 159, 10)
CARD_BG = (18, 19, 24)
CARD_BORDER = (42, 44, 52)

# Load fonts
try:
    FONT_HERO = ImageFont.truetype("segoeuib.ttf", 96)
    FONT_TITLE = ImageFont.truetype("segoeuib.ttf", 64)
    FONT_SUBTITLE = ImageFont.truetype("segoeui.ttf", 36)
    FONT_BODY = ImageFont.truetype("segoeui.ttf", 28)
    FONT_CODE = ImageFont.truetype("consola.ttf", 26)
    FONT_BADGE = ImageFont.truetype("segoeuib.ttf", 22)
    FONT_PRICE = ImageFont.truetype("segoeuib.ttf", 90)
except Exception:
    FONT_HERO = FONT_TITLE = FONT_SUBTITLE = FONT_BODY = FONT_CODE = FONT_BADGE = FONT_PRICE = ImageFont.load_default()

def ease_out_cubic(x):
    return 1 - pow(1 - min(max(x, 0.0), 1.0), 3)

def ease_in_out(x):
    x = min(max(x, 0.0), 1.0)
    return -(math.cos(math.pi * x) - 1) / 2

# Scene definitions: (id, title, duration_seconds, voiceover_text)
SCENES_CONFIG = [
    {
        "id": "INTRO",
        "dur": 9.5,
        "text": "Meet JARVIS. The next generation personal AI executive workstation for Windows."
    },
    {
        "id": "LOCAL_ENGINE",
        "dur": 10.5,
        "text": "Engineered from the ground up for total privacy. Powered by local GPU intelligence with zero cloud data leaks."
    },
    {
        "id": "VISION",
        "dur": 11.5,
        "text": "With real-time vision, JARVIS sees what you see. Analyzing active windows and documents in under fifty milliseconds."
    },
    {
        "id": "DEVICE_CONTROL",
        "dur": 11.5,
        "text": "Order your PC effortlessly. Click options, launch apps, search files, and create complete PowerPoint presentations on command."
    },
    {
        "id": "COMMERCIAL",
        "dur": 11.0,
        "text": "Enterprise capability for everyday creators. Just five dollars a month, with hardware-locked security and instant setup."
    },
    {
        "id": "OUTRO",
        "dur": 11.0,
        "text": "This is JARVIS. Autonomous desktop intelligence, redefined. Available now."
    }
]

async def build_audio_tracks():
    print("[1/3] Synthesizing full synchronized voiceover tracks...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    concat_list_path = os.path.join(TEMP_DIR, "concat_list.txt")
    
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for idx, sc in enumerate(SCENES_CONFIG):
            raw_audio = os.path.join(TEMP_DIR, f"scene_{idx}_raw.mp3")
            padded_audio = os.path.join(TEMP_DIR, f"scene_{idx}_pad.mp3")
            
            comm = edge_tts.Communicate(sc["text"], "en-IN-PrabhatNeural", rate="-2%")
            await comm.save(raw_audio)
            
            # Pad audio with silence to exactly match scene duration
            target_dur = sc["dur"]
            cmd = [
                ffmpeg_exe, "-y",
                "-i", raw_audio,
                "-af", f"apad=whole_dur={target_dur}",
                "-t", str(target_dur),
                padded_audio
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            f.write(f"file '{padded_audio.replace(os.sep, '/')}'\n")

    full_audio = os.path.join(TEMP_DIR, "master_audio.mp3")
    cmd_cat = [
        ffmpeg_exe, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        full_audio
    ]
    subprocess.run(cmd_cat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(" Master voiceover track synchronized successfully.")
    return full_audio

def draw_pill(draw, text, cx, cy, color=ACCENT_BLUE):
    bbox = draw.textbbox((0, 0), text, font=FONT_BADGE)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad_x, pad_y = 20, 8
    x1, y1 = cx - tw//2 - pad_x, cy - th//2 - pad_y
    x2, y2 = cx + tw//2 + pad_x, cy + th//2 + pad_y
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill=(22, 24, 30), outline=(50, 54, 66), width=1)
    draw.text((cx - tw//2, cy - th//2 - 1), text, font=FONT_BADGE, fill=color)

def draw_core_orb(draw, cx, cy, base_r, t):
    pulse = math.sin(t * 3.5) * 6
    r = base_r + pulse
    # Ambient glows
    for i in range(4):
        glow_r = r + i * 22
        alpha_color = (15 + i*8, 40 + i*18, 90 + i*35)
        draw.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r], outline=alpha_color, width=2)
    # Bright ring
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ACCENT_BLUE, width=4)
    # Rotating satellites
    for k in range(3):
        angle = t * 2.0 + k * (2 * math.pi / 3)
        sx = cx + math.cos(angle) * (r + 32)
        sy = cy + math.sin(angle) * (r + 32)
        draw.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=TEXT_WHITE)
    # Inner nucleus
    draw.ellipse([cx - r*0.35, cy - r*0.35, cx + r*0.35, cy + r*0.35], fill=TEXT_WHITE)

def render_scenes_video():
    print("[2/3] Rendering 1080p 60FPS Apple-style Keynote visual timeline...")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(TEMP_VIDEO, fourcc, FPS, (WIDTH, HEIGHT))

    total_scenes = len(SCENES_CONFIG)
    frame_offsets = []
    accum = 0
    for sc in SCENES_CONFIG:
        frame_offsets.append((accum, int(sc["dur"] * FPS)))
        accum += int(sc["dur"] * FPS)
    total_frames = accum

    for f_idx in range(total_frames):
        # Determine active scene
        scene_idx = 0
        local_f = 0
        local_len = 0
        for idx, (start_f, dur_f) in enumerate(frame_offsets):
            if start_f <= f_idx < start_f + dur_f:
                scene_idx = idx
                local_f = f_idx - start_f
                local_len = dur_f
                break

        img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_BLACK)
        draw = ImageDraw.Draw(img)
        t = f_idx / FPS
        sc_prog = local_f / max(1, local_len)
        fade_in = ease_out_cubic(min(1.0, local_f / 45.0))
        fade_out = 1.0 - ease_in_out(max(0.0, (local_f - (local_len - 30)) / 30.0))
        master_alpha = min(fade_in, fade_out)

        # ── SCENE 0: INTRO (0 - 9.5s) ─────────────────────────────────────────
        if scene_idx == 0:
            draw_pill(draw, "THE NEXT GENERATION EXECUTIVE ASSISTANT", WIDTH//2, 240)
            draw_core_orb(draw, WIDTH//2, 470, 75, t)

            title = "J.A.R.V.I.S."
            bbox = draw.textbbox((0, 0), title, font=FONT_HERO)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, 610), title, font=FONT_HERO, fill=TEXT_WHITE)

            sub = "Your Windows PC. Fully Autonomous."
            sbox = draw.textbbox((0, 0), sub, font=FONT_SUBTITLE)
            draw.text((WIDTH//2 - (sbox[2]-sbox[0])//2, 730), sub, font=FONT_SUBTITLE, fill=TEXT_MUTED)

        # ── SCENE 1: LOCAL PRIVACY & GPU ENGINE (9.5 - 20s) ───────────────────
        elif scene_idx == 1:
            draw_pill(draw, "100% PRIVATE • ZERO CLOUD LEAKS", WIDTH//2, 200, ACCENT_GREEN)

            title = "Pure Local Intelligence."
            bbox = draw.textbbox((0, 0), title, font=FONT_TITLE)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, 260), title, font=FONT_TITLE, fill=TEXT_WHITE)

            cards = [
                ("RTX Accelerated", "Direct GPU inference.\nInstant responsiveness\nwithout cloud lag.", ACCENT_BLUE),
                ("Strict Privacy", "Screen scans & memory\nstay strictly on your\nphysical device.", ACCENT_GREEN),
                ("Native Voices", "Authentic English (India)\nneural dialect without\nrobotic distortion.", ACCENT_PURPLE)
            ]
            cw, ch = 420, 290
            xs = [260, 750, 1240]
            for ci, (cx, (chdr, cdesc, ccolor)) in enumerate(zip(xs, cards)):
                entry = ease_out_cubic(min(1.0, max(0.0, (sc_prog - ci * 0.12) / 0.35)))
                y_shift = int((1.0 - entry) * 50)
                draw.rounded_rectangle([cx, 380 + y_shift, cx + cw, 380 + ch + y_shift], radius=20, fill=CARD_BG, outline=CARD_BORDER, width=1)
                draw.text((cx + 36, 420 + y_shift), chdr, font=FONT_SUBTITLE, fill=ccolor)
                draw.text((cx + 36, 490 + y_shift), cdesc, font=FONT_BODY, fill=TEXT_MUTED)

        # ── SCENE 2: REAL-TIME SCREEN VISION (20 - 31.5s) ─────────────────────
        elif scene_idx == 2:
            draw_pill(draw, "SUB-50ms OCR + MULTIMODAL SENSING", WIDTH//2, 180, ACCENT_BLUE)

            title = "It sees what you see."
            bbox = draw.textbbox((0, 0), title, font=FONT_TITLE)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, 240), title, font=FONT_TITLE, fill=TEXT_WHITE)

            # Minimalist Glass Terminal Mockup
            tx1, ty1, tx2, ty2 = 340, 340, WIDTH - 340, 840
            draw.rounded_rectangle([tx1, ty1, tx2, ty2], radius=22, fill=(14, 15, 19), outline=CARD_BORDER, width=1)
            # Title bar
            draw.rounded_rectangle([tx1, ty1, tx2, ty1 + 50], radius=22, fill=(24, 25, 30))
            draw.rectangle([tx1, ty1 + 30, tx2, ty1 + 50], fill=(24, 25, 30))
            draw.ellipse([tx1 + 24, ty1 + 18, tx1 + 38, ty1 + 32], fill=(255, 95, 86))
            draw.ellipse([tx1 + 46, ty1 + 18, tx1 + 60, ty1 + 32], fill=(255, 189, 46))
            draw.ellipse([tx1 + 68, ty1 + 18, tx1 + 82, ty1 + 32], fill=(39, 201, 63))
            draw.text((tx1 + 100, ty1 + 14), "JARVIS Real-Time Vision Pipeline // Active Screen", font=FONT_CODE, fill=TEXT_MUTED)

            lines = [
                ("user", "User: \"Jarvis, what is currently on my display?\""),
                ("sys", "[VISION CORE] Screen grabbed. Windows OCR: 42 text nodes detected in 38ms."),
                ("bot", "JARVIS: \"Sir, you have your presentation editor open on slide 3,"),
                ("bot", "        with a code repository and financial chart visible on the right.\"")
            ]
            for li, (ltype, ltext) in enumerate(lines):
                col = TEXT_WHITE if ltype == "user" else (ACCENT_BLUE if ltype == "sys" else ACCENT_GREEN)
                draw.text((tx1 + 40, ty1 + 80 + li * 55), ltext, font=FONT_BODY, fill=col)

        # ── SCENE 3: COMPLETE DEVICE CONTROL (31.5 - 43s) ─────────────────────
        elif scene_idx == 3:
            draw_pill(draw, "AUTONOMOUS SYSTEM AUTOMATION", WIDTH//2, 180, ACCENT_ORANGE)

            title = "Effortless Device Control."
            bbox = draw.textbbox((0, 0), title, font=FONT_TITLE)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, 240), title, font=FONT_TITLE, fill=TEXT_WHITE)

            items = [
                ("PowerPoint Creation", "Creates formatted, multi-slide presentations and launches PowerPoint.", ACCENT_ORANGE),
                ("Targeted Mouse Clicking", "Locates any UI button, link, or menu and clicks with natural precision.", ACCENT_BLUE),
                ("Multi-Drive File Search", "Indexes 500,000+ files across C:, D:, and E: drives in under 1 second.", ACCENT_PURPLE),
                ("Dual Voice & Typing", "Speak hands-free with Indian English voice or type seamlessly in text mode.", ACCENT_GREEN)
            ]
            for ii, (ititle, idesc, icolor) in enumerate(items):
                iy = 340 + ii * 125
                entry = ease_out_cubic(min(1.0, max(0.0, (sc_prog - ii * 0.1) / 0.35)))
                ix = int(320 + (1.0 - entry) * 60)
                draw.rounded_rectangle([ix, iy, ix + 1280, iy + 100], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=1)
                draw.ellipse([ix + 35, iy + 35, ix + 65, iy + 65], fill=icolor)
                draw.text((ix + 90, iy + 20), ititle, font=FONT_SUBTITLE, fill=TEXT_WHITE)
                draw.text((ix + 90, iy + 58), idesc, font=FONT_BODY, fill=TEXT_MUTED)

        # ── SCENE 4: COMMERCIAL & ACCESSIBLE VALUE (43 - 54s) ──────────────────
        elif scene_idx == 4:
            draw_pill(draw, "TRANSPARENT VALUE • CANCEL ANYTIME", WIDTH//2, 180, ACCENT_GREEN)

            title = "Pro AI. Accessible to everyone."
            bbox = draw.textbbox((0, 0), title, font=FONT_TITLE)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, 240), title, font=FONT_TITLE, fill=TEXT_WHITE)

            card_x1, card_y1 = WIDTH//2 - 320, 330
            card_x2, card_y2 = WIDTH//2 + 320, 830
            draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=24, fill=CARD_BG, outline=ACCENT_BLUE, width=2)

            draw.text((card_x1 + 50, card_y1 + 45), "Commercial Edition", font=FONT_SUBTITLE, fill=TEXT_WHITE)
            draw.text((card_x1 + 50, card_y1 + 95), "Compiled Windows 10 & 11 Protected Binary", font=FONT_BODY, fill=TEXT_MUTED)

            draw.text((card_x1 + 50, card_y1 + 160), "$5", font=FONT_PRICE, fill=TEXT_WHITE)
            draw.text((card_x1 + 175, card_y1 + 215), "/ month", font=FONT_SUBTITLE, fill=TEXT_MUTED)

            bullet_points = [
                "✓ Unlimited Hands-Free Voice & Text Input",
                "✓ Real-Time Screen Vision & Fast OCR",
                "✓ Voice-Ordered Mouse & Keyboard Actions",
                "✓ Instant PowerPoint Slide Deck Builder",
                "✓ Hardware-Locked Tamper Protection"
            ]
            for bi, bp in enumerate(bullet_points):
                draw.text((card_x1 + 50, card_y1 + 285 + bi * 42), bp, font=FONT_BODY, fill=TEXT_WHITE)

        # ── SCENE 5: OUTRO (54 - 65s) ─────────────────────────────────────────
        else:
            draw_core_orb(draw, WIDTH//2, 420, 85, t)

            title = "J.A.R.V.I.S."
            bbox = draw.textbbox((0, 0), title, font=FONT_HERO)
            draw.text((WIDTH//2 - (bbox[2]-bbox[0])//2, 570), title, font=FONT_HERO, fill=TEXT_WHITE)

            sub = "Intelligence, Redefined."
            sbox = draw.textbbox((0, 0), sub, font=FONT_SUBTITLE)
            draw.text((WIDTH//2 - (sbox[2]-sbox[0])//2, 690), sub, font=FONT_SUBTITLE, fill=ACCENT_BLUE)

            cta = "Available Now • Instant Activation"
            cbox = draw.textbbox((0, 0), cta, font=FONT_BODY)
            draw.text((WIDTH//2 - (cbox[2]-cbox[0])//2, 760), cta, font=FONT_BODY, fill=TEXT_WHITE)

        # Write frame
        cv_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(cv_frame)

    out.release()
    print(" Complete visual stream rendered.")

def mux_final_master(full_audio):
    print("[3/3] Muxing master video + full synchronized voiceover track...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y",
        "-i", TEMP_VIDEO,
        "-i", full_audio,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_VIDEO
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # Clean temp video
    if os.path.exists(TEMP_VIDEO):
        os.remove(TEMP_VIDEO)

    print(f"\n Master Keynote Commercial Film ready at:\n{OUTPUT_VIDEO}\n")

if __name__ == "__main__":
    audio_path = asyncio.run(build_audio_tracks())
    render_scenes_video()
    mux_final_master(audio_path)
