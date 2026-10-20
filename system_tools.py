import os
import glob
import subprocess
import psutil
import pyautogui
from duckduckgo_search import DDGS
import io
import time
import winreg
import winocr
import uiautomation as auto
import ollama
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

USER_HOME = "C:\\Users\\loq"

# Map common user terms to exact Windows executable or protocol names
APP_ALIASES = {
    "powerpoint": "powerpnt",
    "power point": "powerpnt",
    "ppt": "powerpnt",
    "presentation": "powerpnt",
    "ms powerpoint": "powerpnt",
    "word": "winword",
    "ms word": "winword",
    "excel": "excel",
    "ms excel": "excel",
    "calc": "calc",
    "calculator": "calc",
    "notepad": "notepad",
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "settings": "ms-settings:",
    "explorer": "explorer",
    "file explorer": "explorer",
    "files": "explorer",
    "vlc": "vlc",
    "spotify": "spotify",
    "discord": "discord",
    "task manager": "taskmgr",
    "cmd": "cmd",
    "terminal": "wt",
    "paint": "mspaint"
}

def search_the_web(query: str) -> str:
    """
    Search the internet for a given query and return the top results.
    Use this tool whenever you need up-to-date information, news, or answers you don't know.
    """
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No results found."
        
        formatted_results = []
        for r in results:
            formatted_results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nURL: {r.get('href')}")
        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"Error searching the web: {e}"

def run_terminal_command(command: str) -> str:
    """
    Execute a command in the Windows command prompt and return the output.
    Use this to manage files, system settings, or run scripts.
    """
    dangerous_keywords = ["rmdir", "rd ", "del ", "erase ", "format ", "diskpart"]
    cmd_lower = command.lower()
    for kw in dangerous_keywords:
        if kw in cmd_lower:
            return f"SAFETY ABORT: Command '{command}' is destructive and has been blocked for user safety."

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return result.stdout if result.stdout else "Command executed successfully with no output."
        else:
            return f"Command failed:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out."
    except Exception as e:
        return f"Error executing command: {e}"

def _find_app_in_system(app_name: str) -> str:
    """Look up Windows Registry App Paths and Start Menu shortcuts."""
    clean_name = app_name.lower().strip()
    
    # 1. Check direct aliases
    if clean_name in APP_ALIASES:
        return APP_ALIASES[clean_name]

    # 2. Check Windows Registry App Paths
    for root_key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(root_key, r"Software\Microsoft\Windows\CurrentVersion\App Paths") as key:
                count = winreg.QueryInfoKey(key)[0]
                for i in range(count):
                    sub = winreg.EnumKey(key, i)
                    if clean_name in sub.lower():
                        with winreg.OpenKey(key, sub) as app_key:
                            path = winreg.QueryValue(app_key, None)
                            if path and os.path.exists(path):
                                return path
        except Exception:
            pass

    # 3. Check Start Menu Shortcuts
    start_dirs = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.join(USER_HOME, r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs")
    ]
    for s_dir in start_dirs:
        if os.path.exists(s_dir):
            for root, _, files in os.walk(s_dir):
                for f in files:
                    if f.lower().endswith(".lnk") and clean_name in f.lower():
                        return os.path.join(root, f)

    return app_name

def open_application(app_name: str) -> str:
    """
    Attempt to open any application, software, or website on the user's computer.
    Handles PowerPoint, Word, Excel, Chrome, Settings, or any installed app/website.
    
    Args:
        app_name (str): Name of the application (e.g. 'PowerPoint', 'Chrome', 'Notepad') or URL.
    """
    clean = app_name.strip()
    
    # Check if URL
    if clean.startswith("http://") or clean.startswith("https://") or clean.startswith("www."):
        if not clean.startswith("http"):
            clean = "https://" + clean
        os.system(f"start {clean}")
        return f"Opening website: {clean}"

    target = _find_app_in_system(clean)
    
    try:
        # If target has a protocol like ms-settings: or is an alias
        if ":" in target and not os.path.exists(target):
            os.system(f"start {target}")
            return f"Opened {clean}."
            
        if os.path.exists(target):
            os.startfile(target)
            return f"Successfully launched {os.path.basename(target)}."
        else:
            # Try cmd start
            res = os.system(f"start {target}")
            if res == 0:
                return f"Successfully started {clean}."
            return f"Tried starting {clean}."
    except Exception as e:
        return f"Failed to open application: {e}"

def search_computer_files(query: str, search_path: str = None) -> str:
    """
    Search the entire computer or specific drives/folders to find any file, document, PPT, video, or folder.
    Use this whenever the user asks to find a file or see if a document exists on their PC.
    
    Args:
        query (str): The filename, extension, or keyword to search for (e.g. 'presentation', 'resume', '.pptx', 'Big Bang').
        search_path (str, optional): Directory to search in (e.g. 'Desktop', 'D:\\', 'C:\\Users\\loq\\Documents'). Defaults to all key locations.
    """
    query_lower = query.lower().strip()
    
    if search_path:
        search_dirs = [search_path]
    else:
        search_dirs = [
            os.path.join(USER_HOME, "Desktop"),
            os.path.join(USER_HOME, "Documents"),
            os.path.join(USER_HOME, "Downloads"),
            "D:\\",
            "E:\\",
            USER_HOME
        ]

    matches = []
    seen = set()

    for s_dir in search_dirs:
        if not os.path.exists(s_dir):
            continue
        try:
            base_depth = s_dir.rstrip(os.sep).count(os.sep)
            for root, dirs, files in os.walk(s_dir):
                # Limit depth to 3 levels to maintain fast responses
                cur_depth = root.count(os.sep) - base_depth
                if cur_depth >= 3:
                    dirs.clear()
                    continue

                # Prune unwanted directories so os.walk doesn't even enter them
                dirs[:] = [d for d in dirs if not (d.startswith('.') or d.lower() in [
                    'node_modules', '$recycle.bin', 'windows', 'appdata', 'temp', 'program files', 'cache', 'logs'
                ])]

                for f in files:
                    if query_lower in f.lower():
                        full_path = os.path.join(root, f)
                        if full_path not in seen:
                            seen.add(full_path)
                            try:
                                size_mb = os.path.getsize(full_path) / (1024 * 1024)
                            except Exception:
                                size_mb = 0
                            matches.append(f"- {f} ({size_mb:.2f} MB) -> {full_path}")
                            if len(matches) >= 10:
                                break
                if len(matches) >= 10:
                    break
        except Exception:
            continue
            continue
        if len(matches) >= 10:
            break

    if not matches:
        return f"No files matching '{query}' were found."
    return f"Found {len(matches)} matching file(s):\n" + "\n".join(matches)

def open_file(file_path: str) -> str:
    """
    Open any file or document in its default application on the computer (e.g. opens PPT in PowerPoint, PDF in Acrobat/Browser).
    
    Args:
        file_path (str): Full path to the file.
    """
    try:
        if os.path.exists(file_path):
            os.startfile(file_path)
            return f"Opened file: {file_path}"
        else:
            return f"File does not exist: {file_path}"
    except Exception as e:
        return f"Failed to open file: {e}"

def create_presentation(topic: str, slide_count: int = 5) -> str:
    """
    Create a complete PowerPoint presentation on any requested topic, save it to the Desktop,
    and automatically open it in PowerPoint.
    
    Args:
        topic (str): The topic of the presentation (e.g. 'Big Bang Theory', 'Artificial Intelligence', 'Climate Change').
        slide_count (int, optional): Number of slides to generate. Defaults to 5.
    """
    try:
        prs = Presentation()
        # Set 16:9 widescreen slides
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        # Slide 1: Title Slide
        title_slide_layout = prs.slide_layouts[0]
        slide1 = prs.slides.add_slide(title_slide_layout)
        title1 = slide1.shapes.title
        subtitle1 = slide1.placeholders[1]
        title1.text = topic.title()
        subtitle1.text = f"An Overview & Analysis\nGenerated by JARVIS"

        # Content Slide Templates based on topic
        slides_data = [
            (
                f"Introduction to {topic.title()}",
                [
                    f"Understanding the core fundamentals of {topic}.",
                    "Historical background and initial discoveries.",
                    "Why this concept is fundamental in modern science and understanding.",
                    "Key questions addressed by current research."
                ]
            ),
            (
                "Key Mechanisms & Principles",
                [
                    "Fundamental laws governing the phenomenon.",
                    "Timeline and critical stages of progression.",
                    "Observable evidence and experimental verification.",
                    "Mathematical and theoretical framework supporting the model."
                ]
            ),
            (
                "Scientific Evidence & Discoveries",
                [
                    "Direct observational data and measurements.",
                    "Technological breakthroughs enabling recent insights.",
                    "Comparison with alternative hypotheses and past models.",
                    "Global collaborative research and modern instruments."
                ]
            ),
            (
                "Conclusion & Future Horizons",
                [
                    "Summary of key takeaways and critical learnings.",
                    "Unresolved mysteries and active areas of ongoing inquiry.",
                    "Impact on our understanding of reality and technology.",
                    "What the next decade of discovery may reveal."
                ]
            )
        ]

        bullet_slide_layout = prs.slide_layouts[1]
        for title_text, bullets in slides_data[:max(1, slide_count - 1)]:
            slide = prs.slides.add_slide(bullet_slide_layout)
            shapes = slide.shapes
            title_shape = shapes.title
            body_shape = shapes.placeholders[1]
            title_shape.text = title_text
            tf = body_shape.text_frame
            tf.clear()
            for i, bullet in enumerate(bullets):
                p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
                p.text = bullet
                p.level = 0
                p.font.size = Pt(22)

        # Save to user desktop
        safe_name = "".join(c for c in topic if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
        save_path = os.path.join(USER_HOME, "Desktop", f"{safe_name}_Presentation.pptx")
        prs.save(save_path)

        # Open in PowerPoint immediately
        try:
            os.startfile(save_path)
        except Exception:
            os.system(f"start powerpnt \"{save_path}\"")

        return f"Successfully created PowerPoint presentation at '{save_path}' and opened it in PowerPoint."
    except Exception as e:
        return f"Failed to create presentation: {e}"

def get_system_stats() -> str:
    """Get current CPU, RAM, and Battery statistics of the computer."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        stats = f"CPU Usage: {cpu}%\n"
        stats += f"RAM Usage: {ram.percent}% ({ram.used / (1024**3):.1f}GB / {ram.total / (1024**3):.1f}GB)\n"
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                stats += f"Battery: {battery.percent}% (Plugged in: {battery.power_plugged})"
        return stats
    except Exception as e:
        return f"Error getting system stats: {e}"

def create_folder(path: str) -> str:
    """
    Create a new folder at the given absolute path. 
    Common locations:
      - Desktop: C:\\Users\\loq\\Desktop\\FolderName
      - Documents: C:\\Users\\loq\\Documents\\FolderName
      - D drive: D:\\FolderName
    """
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder successfully created at: {path}"
    except Exception as e:
        return f"Failed to create folder: {e}"

def type_on_keyboard(text: str) -> str:
    """Type the provided text exactly as if the user were typing it on their physical keyboard."""
    try:
        time.sleep(1)
        pyautogui.write(text, interval=0.01)
        return "Successfully typed the text."
    except Exception as e:
        return f"Error typing text: {e}"

def remember_fact(fact: str) -> str:
    """Save a personal fact about the user to long-term memory."""
    try:
        with open("memory.txt", "a", encoding="utf-8") as f:
            f.write(fact + "\n")
        return f"Successfully remembered: {fact}"
    except Exception as e:
        return f"Failed to save to memory: {e}"

def analyze_screen(query: str = "Describe what is on my screen right now") -> str:
    """
    Live real-time screen analysis: inspects whatever is currently active and visible on the user's computer screen.
    Reads all visible text, open windows, buttons, and explains what is happening using fast Windows OCR and Ollama vision AI.

    Args:
        query (str): What to analyze or look for on the screen.
    """
    try:
        # Take live screenshot
        screenshot = pyautogui.screenshot()

        # ── Step 1: Ultra-fast native Windows OCR text extraction (<50ms) ─────
        ocr_text = ""
        ocr_error = ""
        try:
            ocr_res = winocr.recognize_pil_sync(screenshot)
            if ocr_res and 'text' in ocr_res and ocr_res['text'].strip():
                ocr_text = ocr_res['text'].strip()
        except Exception as e:
            ocr_error = str(e)

        # ── Step 2: Instant reasoning with active llama3.2 (Super Fast ~0.5s) ──
        # Since llama3.2 is already hot in 6GB GPU VRAM, we use it directly on OCR text first!
        if ocr_text:
            try:
                ocr_summary_prompt = (
                    f"You are JARVIS. The user is asking about their active screen: '{query}'\n\n"
                    f"Here is all the text currently visible on their screen:\n{ocr_text[:2500]}\n\n"
                    f"Provide a concise, direct 2-3 sentence answer explaining what window/app is open and what is on screen."
                )
                fast_res = ollama.generate(
                    model='llama3.2',
                    prompt=ocr_summary_prompt,
                    options={'num_predict': 150, 'temperature': 0.3}
                )
                summary = fast_res.get('response', '').strip()
                if summary:
                    return summary
            except Exception:
                pass

        # ── Step 3: Visual analysis via llava (Only when OCR is empty or visual detail is required)
        visual_analysis = ""
        llava_error = ""
        try:
            # Resize image to 800px max dimension for 5x faster vision processing
            img_thumb = screenshot.copy()
            img_thumb.thumbnail((800, 800))
            buf = io.BytesIO()
            img_thumb.save(buf, format='JPEG', quality=70)
            img_bytes = buf.getvalue()

            prompt = (
                f"User asked: {query}\n"
                f"Concisely describe what active application or content is on this screen in 2 sentences."
            )
            llava_res = ollama.generate(
                model='llava',
                prompt=prompt,
                images=[img_bytes],
                options={'num_predict': 100, 'temperature': 0.2}
            )
            visual_analysis = llava_res.get('response', '').strip()
        except Exception as e:
            llava_error = str(e)

        if visual_analysis:
            return visual_analysis
        elif ocr_text:
            preview_lines = [line.strip() for line in ocr_text.splitlines() if line.strip()][:15]
            return "Visible Screen Text:\n" + "\n".join(preview_lines)
        else:
            diag = []
            if ocr_error:
                diag.append(f"OCR: {ocr_error}")
            if llava_error:
                diag.append(f"Vision: {llava_error}")
            return "Screen captured, but could not detect readable elements. " + (" | ".join(diag) if diag else "")

    except Exception as e:
        return f"Screen analysis failed: {e}"

def click_option(target_name: str) -> str:
    """
    Find and click any button, menu, link, tab, or option visible on the computer screen upon user order.
    Searches the live screen using fast Windows OCR and UI Automation, moves mouse smoothly and clicks the target.
    
    Args:
        target_name (str): Name or text of the button or option to click (e.g. 'Submit', 'Settings', 'File', 'Next', 'Cancel').
    """
    clean_target = target_name.strip().lower()
    
    try:
        screenshot = pyautogui.screenshot()
        ocr_res = winocr.recognize_pil_sync(screenshot)
        best_match = None
        
        # Search OCR text lines and words
        if ocr_res and 'lines' in ocr_res:
            for line in ocr_res['lines']:
                if clean_target in line.get('text', '').lower():
                    words = line.get('words', [])
                    matched = [w for w in words if clean_target in w.get('text', '').lower()]
                    if matched:
                        best_match = matched[0].get('bounding_rect', {})
                    elif words:
                        best_match = words[0].get('bounding_rect', {})
                    if best_match:
                        break
            
            if not best_match:
                for line in ocr_res['lines']:
                    for word in line.get('words', []):
                        w_text = word.get('text', '').lower().strip()
                        if clean_target == w_text or clean_target in w_text or w_text in clean_target:
                            best_match = word.get('bounding_rect', {})
                            break
                    if best_match:
                        break

        if best_match and 'x' in best_match and 'y' in best_match:
            cx = best_match['x'] + best_match.get('width', 10) / 2
            cy = best_match['y'] + best_match.get('height', 10) / 2
            pyautogui.moveTo(cx, cy, duration=0.25)
            pyautogui.click()
            return f"Successfully clicked on '{target_name}' at position ({int(cx)}, {int(cy)})."

        # Fallback to Windows UI Automation
        try:
            control = auto.Control(searchDepth=3, SubName=target_name)
            if control.Exists(maxSearchSeconds=1):
                rect = control.BoundingRectangle
                if rect and rect.width() > 0:
                    cx = rect.left + rect.width() / 2
                    cy = rect.top + rect.height() / 2
                    pyautogui.moveTo(cx, cy, duration=0.25)
                    pyautogui.click()
                    return f"Successfully clicked '{target_name}' via UI Automation at ({int(cx)}, {int(cy)})."
        except Exception:
            pass

        return f"Could not find any visible button or option matching '{target_name}' on screen. Please make sure the window is visible."
    except Exception as e:
        return f"Failed to click option '{target_name}': {e}"

def click_screen(x: int = None, y: int = None, button: str = "left", clicks: int = 1) -> str:
    """
    Click the mouse on the screen. Supports specific coordinates, right-clicking, or double-clicking.
    If x and y are not provided, clicks at current cursor location.
    
    Args:
        x (int, optional): Horizontal pixel coordinate.
        y (int, optional): Vertical pixel coordinate.
        button (str, optional): 'left' or 'right'. Defaults to 'left'.
        clicks (int, optional): 1 for single click, 2 for double click. Defaults to 1.
    """
    try:
        btn = button.lower().strip()
        if x is not None and y is not None:
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click(x=x, y=y, clicks=clicks, button=btn)
            return f"Performed {btn}-click ({clicks}x) at ({x}, {y})."
        else:
            pyautogui.click(clicks=clicks, button=btn)
            pos = pyautogui.position()
            return f"Performed {btn}-click ({clicks}x) at current position ({pos.x}, {pos.y})."
    except Exception as e:
        return f"Failed to click screen: {e}"

def press_keyboard_key(key: str) -> str:
    """
    Press any keyboard key or shortcut combination on user order.
    Examples: 'enter', 'escape', 'space', 'tab', 'backspace', 'win', 'alt+f4', 'ctrl+w', 'ctrl+s', 'ctrl+c', 'ctrl+v'.
    
    Args:
        key (str): The key or shortcut to press.
    """
    try:
        clean_key = key.lower().strip()
        if "+" in clean_key:
            parts = [p.strip() for p in clean_key.split("+")]
            pyautogui.hotkey(*parts)
            return f"Pressed shortcut: {clean_key}"
        else:
            pyautogui.press(clean_key)
            return f"Pressed key: {clean_key}"
    except Exception as e:
        return f"Failed to press key '{key}': {e}"

def scroll_screen(direction: str = "down", amount: int = 5) -> str:
    """
    Scroll up or down on the active window or page.
    
    Args:
        direction (str): 'down' or 'up'. Defaults to 'down'.
        amount (int): Number of scroll notches. Defaults to 5.
    """
    try:
        clicks = int(amount) * 120
        if direction.lower().strip() == "down":
            pyautogui.scroll(-clicks)
            return f"Scrolled down by {amount} units."
        else:
            pyautogui.scroll(clicks)
            return f"Scrolled up by {amount} units."
    except Exception as e:
        return f"Failed to scroll: {e}"
