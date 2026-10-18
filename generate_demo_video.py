"""
JARVIS Autonomous Product Demo Video Generator
Renders a 1080p Full HD motion-graphics demo video showcasing all JARVIS features.
"""

import os
import cv2
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1920, 1080
FPS = 30
OUTPUT_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "JARVIS_Demo_Video.mp4")

# Color palette
BG_DARK = (10, 14, 23)
CYAN = (0, 240, 255)
BLUE = (0, 120, 255)
GREEN = (0, 255, 150)
PURPLE = (180, 50, 255)
WHITE = (255, 255, 255)
GRAY = (150, 160, 180)
CARD_BG = (18, 24, 38)
ACCENT_ORANGE = (255, 140, 0)

# Load fonts
try:
    FONT_TITLE = ImageFont.truetype("segoeuib.ttf", 75)
    FONT_SUBTITLE = ImageFont.truetype("segoeui.ttf", 36)
    FONT_BODY = ImageFont.truetype("segoeui.ttf", 30)
    FONT_BOLD = ImageFont.truetype("segoeuib.ttf", 34)
    FONT_CODE = ImageFont.truetype("consola.ttf", 26)
    FONT_BIG = ImageFont.truetype("segoeuib.ttf", 110)
    FONT_PRICE = ImageFont.truetype("segoeuib.ttf", 90)
except Exception:
    FONT_TITLE = FONT_SUBTITLE = FONT_BODY = FONT_BOLD = FONT_CODE = FONT_BIG = FONT_PRICE = ImageFont.load_default()

def draw_hud_background(draw, frame_idx):
    """Draws a subtle cyber grid and corner HUD markings."""
    # Subtle grid lines
    grid_spacing = 80
    for x in range(0, WIDTH, grid_spacing):
        draw.line([(x, 0), (x, HEIGHT)], fill=(16, 22, 34), width=1)
    for y in range(0, HEIGHT, grid_spacing):
        draw.line([(0, y), (WIDTH, y)], fill=(16, 22, 34), width=1)

    # Top & bottom accent lines
    draw.line([(60, 40), (WIDTH - 60, 40)], fill=(0, 180, 220), width=2)
    draw.line([(60, HEIGHT - 40), (WIDTH - 60, HEIGHT - 40)], fill=(0, 180, 220), width=2)

    # Tech header
    draw.text((80, 16), "SYSTEM STATUS: OPERATIONAL // RTX 4050 ACCELERATED", font=FONT_CODE, fill=(0, 220, 255))
    draw.text((WIDTH - 360, 16), "J.A.R.V.I.S. OS v2.4", font=FONT_CODE, fill=(0, 220, 255))

    # Corner brackets
    bracket_len = 30
    for cx, cy in [(60, 60), (WIDTH - 60, 60), (60, HEIGHT - 60), (WIDTH - 60, HEIGHT - 60)]:
        dx = 1 if cx < WIDTH // 2 else -1
        dy = 1 if cy < HEIGHT // 2 else -1
        draw.line([(cx, cy), (cx + dx * bracket_len, cy)], fill=CYAN, width=3)
        draw.line([(cx, cy), (cx, cy + dy * bracket_len)], fill=CYAN, width=3)

def draw_arc_reactor(draw, cx, cy, radius, frame_idx):
    """Draws an animated pulsing AI Core."""
    pulse = math.sin(frame_idx * 0.1) * 8
    r = radius + pulse

    # Outer spinning dashes
    for i in range(12):
        angle = (frame_idx * 2 + i * 30) * math.pi / 180
        x1 = cx + math.cos(angle) * (r + 20)
        y1 = cy + math.sin(angle) * (r + 20)
        x2 = cx + math.cos(angle) * (r + 35)
        y2 = cy + math.sin(angle) * (r + 35)
        draw.line([(x1, y1), (x2, y2)], fill=CYAN, width=4)

    # Glowing circles
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=BLUE, width=5)
    draw.ellipse([(cx - r*0.7, cy - r*0.7), (cx + r*0.7, cy + r*0.7)], outline=CYAN, width=4)
    draw.ellipse([(cx - r*0.35, cy - r*0.35), (cx + r*0.35, cy + r*0.35)], fill=(0, 230, 255))

def render_scene_1(frame_idx, total_frames):
    """Scene 1: Epic Title Reveal (0 - 4s)"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_hud_background(draw, frame_idx)

    # Pulsing core
    draw_arc_reactor(draw, WIDTH // 2, 420, 110, frame_idx)

    # Title with glow simulation
    draw.text((WIDTH // 2 - 320, 580), "J. A. R. V. I. S.", font=FONT_BIG, fill=CYAN)
    draw.text((WIDTH // 2 - 420, 710), "Autonomous Local AI Assistant for Windows", font=FONT_SUBTITLE, fill=WHITE)
    draw.text((WIDTH // 2 - 460, 780), "100% Offline GPU Inference  •  Vision & Screen Control  •  Hands-Free Voice", font=FONT_BODY, fill=GRAY)

    # Badge
    badge_rect = [(WIDTH // 2 - 160, 860), (WIDTH // 2 + 160, 915)]
    draw.rounded_rectangle(badge_rect, radius=12, fill=(0, 80, 140), outline=CYAN, width=2)
    draw.text((WIDTH // 2 - 135, 872), "POWERED BY LLAMA 3.2", font=FONT_CODE, fill=WHITE)
    return img

def render_scene_2(frame_idx, total_frames):
    """Scene 2: Live Hands-Free Voice Control (4s - 8s)"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_hud_background(draw, frame_idx)

    draw.text((120, 100), "01 // HANDS-FREE VOICE INTELLIGENCE", font=FONT_TITLE, fill=CYAN)
    draw.text((120, 180), "Continuous ambient voice listening with instant local speech recognition", font=FONT_SUBTITLE, fill=GRAY)

    # Audio waveform visualization
    cx = WIDTH // 2
    cy = 460
    num_bars = 48
    bar_width = 12
    spacing = 22
    start_x = cx - (num_bars * spacing) // 2

    for i in range(num_bars):
        h = abs(math.sin(frame_idx * 0.15 + i * 0.3)) * 140 + 20
        x = start_x + i * spacing
        color = CYAN if i % 2 == 0 else GREEN
        draw.rounded_rectangle([(x, cy - h // 2), (x + bar_width, cy + h // 2)], radius=6, fill=color)

    # Simulated Live Transcript Card
    card_rect = [(240, 620), (WIDTH - 240, 880)]
    draw.rounded_rectangle(card_rect, radius=20, fill=CARD_BG, outline=BLUE, width=3)

    draw.text((280, 650), "🗣️ You:", font=FONT_BOLD, fill=CYAN)
    draw.text((430, 652), "\"Jarvis, create a complete presentation on the Big Bang topic.\"", font=FONT_BODY, fill=WHITE)

    draw.line([(280, 730), (WIDTH - 280, 730)], fill=(30, 45, 65), width=2)

    draw.text((280, 760), "🤖 JARVIS:", font=FONT_BOLD, fill=GREEN)
    draw.text((430, 762), "\"Ji sir! Creating your PowerPoint presentation and launching it now.\"", font=FONT_BODY, fill=WHITE)

    # Language pill badges
    draw.rounded_rectangle([(WIDTH - 540, 650), (WIDTH - 300, 695)], radius=10, fill=(0, 60, 40), outline=GREEN, width=1)
    draw.text((WIDTH - 520, 660), "● English / Hindi / Hinglish", font=FONT_CODE, fill=GREEN)
    return img

def render_scene_3(frame_idx, total_frames):
    """Scene 3: Autonomous PowerPoint Creation (8s - 13s)"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_hud_background(draw, frame_idx)

    draw.text((120, 100), "02 // AUTONOMOUS OFFICE & PRESENTATION GENERATOR", font=FONT_TITLE, fill=CYAN)
    draw.text((120, 180), "Builds formatted slide decks and opens Microsoft PowerPoint instantly upon voice order", font=FONT_SUBTITLE, fill=GRAY)

    # Left Card: Slide Outline
    left_card = [(140, 260), (740, 920)]
    draw.rounded_rectangle(left_card, radius=16, fill=CARD_BG, outline=CYAN, width=2)
    draw.text((180, 290), "Generated Slide Outline", font=FONT_BOLD, fill=CYAN)

    slides = [
        "1. Title: The Big Bang Theory",
        "2. Core Fundamentals & Initial Expansion",
        "3. Key Mechanisms & Cosmic Inflation",
        "4. Observational Evidence & CMB Radiation",
        "5. Future Horizons & Ongoing Mysteries"
    ]
    for idx, s in enumerate(slides):
        y = 370 + idx * 100
        # Checkbox icon
        draw.rounded_rectangle([(180, y), (215, y + 35)], radius=6, fill=GREEN)
        draw.text((188, y + 2), "✓", font=FONT_BOLD, fill=(10, 20, 30))
        draw.text((240, y + 3), s, font=FONT_BODY, fill=WHITE)

    # Right Card: Simulated PowerPoint Slide Preview
    right_card = [(800, 260), (WIDTH - 140, 920)]
    draw.rounded_rectangle(right_card, radius=16, fill=(24, 30, 45), outline=ACCENT_ORANGE, width=3)

    # Top PPT Header Bar
    draw.rectangle([(800, 260), (WIDTH - 140, 320)], fill=(196, 62, 28)) # Office Orange
    draw.text((830, 275), "Microsoft PowerPoint  —  Big_Bang_Presentation.pptx", font=FONT_BOLD, fill=WHITE)

    # Slide canvas area
    draw.rectangle([(860, 360), (WIDTH - 200, 870)], fill=(12, 16, 26), outline=(60, 70, 90), width=2)
    draw.text((940, 420), "THE BIG BANG THEORY", font=FONT_TITLE, fill=CYAN)
    draw.text((940, 520), "Cosmic Origins & Fundamental Forces", font=FONT_SUBTITLE, fill=WHITE)
    draw.line([(940, 580), (1400, 580)], fill=CYAN, width=3)

    bullets = [
        "• Originated ~13.8 billion years ago from a hot, dense singularity",
        "• Rapid cosmic inflation expanded space faster than light",
        "• Cosmic Microwave Background verified by COBE & WMAP",
        "• Automatically authored and formatted by JARVIS"
    ]
    for idx, b in enumerate(bullets):
        draw.text((940, 620 + idx * 55), b, font=FONT_BODY, fill=GRAY)

    # Success popup badge
    draw.rounded_rectangle([(WIDTH - 500, 800), (WIDTH - 220, 850)], radius=12, fill=(0, 140, 70))
    draw.text((WIDTH - 480, 812), "✓ Presentation Saved to Desktop", font=FONT_CODE, fill=WHITE)
    return img

def render_scene_4(frame_idx, total_frames):
    """Scene 4: Live Screen Vision & Real-Time Clicking (13s - 18s)"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_hud_background(draw, frame_idx)

    draw.text((120, 100), "03 // LIVE SCREEN VISION & DEVICE CLICKING", font=FONT_TITLE, fill=CYAN)
    draw.text((120, 180), "Understands your active screen with OCR + Vision AI, and clicks any option on your order", font=FONT_SUBTITLE, fill=GRAY)

    # Big Mock Desktop Screen Area
    desktop_rect = [(200, 260), (WIDTH - 200, 880)]
    draw.rounded_rectangle(desktop_rect, radius=20, fill=(18, 22, 32), outline=BLUE, width=3)

    # Windows title bar
    draw.rectangle([(200, 260), (WIDTH - 200, 310)], fill=(30, 38, 54))
    draw.text((230, 275), "Application Workspace  //  Live Tracking Active", font=FONT_CODE, fill=GRAY)

    # Laser scanner line moving vertically
    scan_y = 330 + int((frame_idx * 12) % 520)
    draw.line([(205, scan_y), (WIDTH - 205, scan_y)], fill=(0, 255, 200), width=3)

    # Detected UI elements with bounding boxes
    elements = [
        ("File Menu", 280, 380, 180, 60),
        ("Settings", 520, 380, 200, 60),
        ("Export PDF", 780, 380, 220, 60),
        ("Submit Order", 1200, 680, 260, 80)
    ]

    for name, ex, ey, ew, eh in elements:
        # Bounding box
        draw.rectangle([(ex, ey), (ex + ew, ey + eh)], outline=CYAN, width=2)
        draw.text((ex + 10, ey - 25), f"OCR: {name}", font=FONT_CODE, fill=CYAN)

    # Animated cursor clicking on "Settings"
    target_x = 520 + 100
    target_y = 380 + 30
    draw.ellipse([(target_x - 35, target_y - 35), (target_x + 35, target_y + 35)], outline=GREEN, width=4)
    # Cursor arrow
    draw.polygon([(target_x, target_y), (target_x + 25, target_y + 35), (target_x + 8, target_y + 30), (target_x, target_y + 40)], fill=WHITE, outline=(0, 0, 0))

    # Real-time action card at bottom
    bot_card = [(400, 790), (WIDTH - 400, 860)]
    draw.rounded_rectangle(bot_card, radius=12, fill=(0, 40, 70), outline=GREEN, width=2)
    draw.text((430, 810), "⚡ Action Executed: Target 'Settings' located at (620, 410) -> Clicked successfully", font=FONT_BOLD, fill=WHITE)
    return img

def render_scene_5(frame_idx, total_frames):
    """Scene 5: Commercial License & Monetization ($5/mo) (18s - 24s)"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_hud_background(draw, frame_idx)

    draw.text((120, 100), "04 // READY TO DISTRIBUTE & MONETIZE", font=FONT_TITLE, fill=CYAN)
    draw.text((120, 180), "Compiled native binary with HWID-bound anti-piracy licensing ($5/month)", font=FONT_SUBTITLE, fill=GRAY)

    # Left: Security features list
    left_box = [(160, 260), (840, 880)]
    draw.rounded_rectangle(left_box, radius=18, fill=CARD_BG, outline=CYAN, width=2)
    draw.text((200, 300), "Built-in Security Architecture", font=FONT_BOLD, fill=CYAN)

    points = [
        ("🔒 Compiled Native Binary (.exe)", "Source code is stripped and compiled into C++ machine code."),
        ("🛡️ Hardware ID (HWID) Locked", "License binds permanently to the customer's specific PC."),
        ("💳 Lemon Squeezy Payments", "Recurring $5/mo subscriptions with automatic license activation."),
        ("👁️ Real-Time Vision & OCR", "Reads any screen in 30ms and acts on voice orders."),
        ("🧠 Autonomous Memory", "Never forgets user details across sessions.")
    ]

    for idx, (title, desc) in enumerate(points):
        y = 390 + idx * 95
        draw.text((200, y), title, font=FONT_BOLD, fill=GREEN)
        draw.text((200, y + 38), desc, font=FONT_CODE, fill=GRAY)

    # Right: Pricing Card
    right_box = [(900, 260), (WIDTH - 160, 880)]
    draw.rounded_rectangle(right_box, radius=18, fill=(16, 26, 44), outline=GREEN, width=4)

    draw.text((1050, 320), "COMMERCIAL LICENSE", font=FONT_BOLD, fill=WHITE)
    draw.text((1020, 420), "$5", font=FONT_PRICE, fill=GREEN)
    draw.text((1180, 460), "/ month", font=FONT_TITLE, fill=GRAY)

    draw.line([(960, 560), (WIDTH - 220, 560)], fill=(40, 60, 85), width=2)

    specs = [
        "✓ Unlimited Voice AI Commands",
        "✓ Real-Time Screen Vision & Analysis",
        "✓ Voice-Activated Device Clicking",
        "✓ Automated PowerPoint Generation",
        "✓ Dedicated Customer License Key"
    ]
    for idx, sp in enumerate(specs):
        draw.text((980, 600 + idx * 50), sp, font=FONT_BODY, fill=WHITE)

    return img

def render_scene_6(frame_idx, total_frames):
    """Scene 6: Outro / Call to Action (24s - 28s)"""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_hud_background(draw, frame_idx)

    draw_arc_reactor(draw, WIDTH // 2, 340, 100, frame_idx)

    draw.text((WIDTH // 2 - 320, 480), "J. A. R. V. I. S.", font=FONT_BIG, fill=CYAN)
    draw.text((WIDTH // 2 - 380, 610), "Your Personal AI Executive Assistant", font=FONT_TITLE, fill=WHITE)

    # Commercial CTA Box
    cta_box = [(WIDTH // 2 - 460, 720), (WIDTH // 2 + 460, 810)]
    draw.rounded_rectangle(cta_box, radius=16, fill=(0, 60, 100), outline=CYAN, width=3)
    draw.text((WIDTH // 2 - 390, 745), "GET JARVIS AI // AVAILABLE FOR WINDOWS 10 & 11", font=FONT_BOLD, fill=WHITE)

    draw.text((WIDTH // 2 - 300, 870), "Commercial Edition • $5/Month • Instant Access", font=FONT_SUBTITLE, fill=GRAY)
    return img

def generate_video():
    print(f">> Starting JARVIS Demo Video Rendering (1080p Full HD @ {FPS} FPS)...")
    print(f"Target file: {OUTPUT_FILE}")

    scenes = [
        (render_scene_1, 4 * FPS),   # 0s - 4s: Title
        (render_scene_2, 4 * FPS),   # 4s - 8s: Voice Control
        (render_scene_3, 5 * FPS),   # 8s - 13s: PowerPoint Creation
        (render_scene_4, 5 * FPS),   # 13s - 18s: Screen Vision & Clicking
        (render_scene_5, 5 * FPS),   # 18s - 23s: $5/mo Monetization
        (render_scene_6, 4 * FPS),   # 23s - 27s: Outro & Call to Action
    ]

    total_video_frames = sum(count for _, count in scenes)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (WIDTH, HEIGHT))

    current_frame = 0
    for scene_idx, (scene_func, frame_count) in enumerate(scenes):
        print(f"Rendering Scene {scene_idx + 1}/{len(scenes)} ({frame_count} frames)...")
        for f in range(frame_count):
            pil_img = scene_func(f, frame_count)
            # Convert PIL RGB to OpenCV BGR
            cv_frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            out.write(cv_frame)
            current_frame += 1

    out.release()
    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print("=" * 60)
    print(f"Demo Video Successfully Generated!")
    print(f"Location: {OUTPUT_FILE}")
    print(f"Resolution: 1920x1080 Full HD | Duration: {total_video_frames // FPS}s | Size: {size_mb:.2f} MB")
    print("=" * 60)

if __name__ == "__main__":
    generate_video()
