import os
os.environ["OLLAMA_MODELS"] = r"E:\ai-image-saas\ollama_models"
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import ollama
import sys
import re
import io
import asyncio
import edge_tts
import pyttsx3
import pygame
import speech_recognition as sr
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from system_tools import (
    search_the_web,
    run_terminal_command,
    open_application,
    get_system_stats,
    type_on_keyboard,
    remember_fact,
    create_folder,
    create_presentation,
    search_computer_files,
    open_file,
    analyze_screen,
    click_option,
    click_screen,
    press_keyboard_key,
    scroll_screen
)
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
from voice_manager import voice_picker

console = Console()
MODEL = "llama3.2"

# ---------------------------------------------------------------------------
# VOICE SYSTEM INITIALIZATION
# ---------------------------------------------------------------------------
pygame.mixer.init()

# ElevenLabs client (only created if API key is provided)
_eleven_client = None
_active_voice_id = ELEVENLABS_VOICE_ID
_active_voice_name = "Default"

if ELEVENLABS_API_KEY:
    try:
        _eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

        # Verify the configured voice ID exists. If not, auto-pick first available.
        import requests as _req
        _resp = _req.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=10
        )
        if _resp.status_code == 200:
            _voices = _resp.json().get("voices", [])
            _voice_ids = {v["voice_id"]: v["name"] for v in _voices}

            if ELEVENLABS_VOICE_ID in _voice_ids:
                _active_voice_id = ELEVENLABS_VOICE_ID
                _active_voice_name = _voice_ids[ELEVENLABS_VOICE_ID]
            elif _voices:
                # Configured voice not found — use first available and save it to config
                _active_voice_id = _voices[0]["voice_id"]
                _active_voice_name = _voices[0]["name"]
                console.print(f"[yellow]⚠️  Voice '{ELEVENLABS_VOICE_ID}' not found. Auto-selecting: [bold]{_active_voice_name}[/bold][/yellow]")
                # Persist fix to config.py so this never happens again
                from voice_manager import update_voice_in_config
                update_voice_in_config(_active_voice_id, _active_voice_name)
                console.print(f"[dim]✅ Saved '{_active_voice_name}' to config.py permanently.[/dim]")
            else:
                console.print("[yellow]⚠️  No voices found in your ElevenLabs account.[/yellow]")
                _eleven_client = None
        else:
            console.print(f"[yellow]⚠️  Could not fetch ElevenLabs voices. Using built-in voice.[/yellow]")
            _eleven_client = None

        if _eleven_client:
            console.print(f"[bold green]✅ ElevenLabs voice active: {_active_voice_name}[/bold green]")
    except Exception as e:
        console.print(f"[yellow]⚠️  ElevenLabs init failed: {e}. Using built-in voice.[/yellow]")
        _eleven_client = None

# Fallback: Windows built-in TTS via pyttsx3
_pyttsx3_engine = None
try:
    _pyttsx3_engine = pyttsx3.init()
    _pyttsx3_engine.setProperty('rate', 165)
    voices = _pyttsx3_engine.getProperty('voices')
    for v in voices:
        if "David" in v.name or "Zira" in v.name:
            _pyttsx3_engine.setProperty('voice', v.id)
            break
except Exception:
    pass

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8
recognizer.non_speaking_duration = 0.4

def clean_text_for_speech(text):
    """Clean markdown so it sounds natural when spoken."""
    text = re.sub(r'```.*?```', ' I have executed the code. ', text, flags=re.DOTALL)
    text = text.replace('*', '').replace('#', '')
    text = re.sub(r'http\S+', 'a link', text)
    return text.strip()

def _speak_elevenlabs(clean_text: str) -> bool:
    """Try to speak using ElevenLabs. Returns True on success, False on failure."""
    if not _eleven_client:
        return False
    try:
        audio_generator = _eleven_client.text_to_speech.convert(
            voice_id=_active_voice_id,
            text=clean_text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
        )
        # Collect all chunks into a buffer
        audio_bytes = b"".join(audio_generator)
        audio_buffer = io.BytesIO(audio_bytes)
        audio_buffer.seek(0)
        pygame.mixer.music.load(audio_buffer, "mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        return True
    except Exception as e:
        err = str(e).lower()
        if "quota" in err or "limit" in err or "billing" in err or "unauthorized" in err:
            console.print("[yellow]⚠️  ElevenLabs quota exhausted or key invalid. Switching to built-in voice.[/yellow]")
        else:
            console.print(f"[dim]ElevenLabs error: {e}[/dim]")
        return False

def is_hindi_or_hinglish(text: str) -> bool:
    """Detect if text contains Hindi characters or common Hinglish words."""
    # Check for Devanagari script
    if re.search(r'[\u0900-\u097F]', text):
        return True
    # Common Hindi/Hinglish marker words
    hindi_keywords = {
        'aap', 'aapko', 'aapka', 'aapki', 'main', 'mera', 'meri', 'mere', 'kya', 'hai', 'hain', 'ho',
        'karna', 'karo', 'kaise', 'batao', 'dijiye', 'karein', 'shukriya', 'theek', 'namaste',
        'madad', 'dhanyawad', 'koshish', 'aur', 'nahi', 'nahin', 'sakte', 'sakta', 'baat',
        'kar', 'raha', 'rahi', 'rahe', 'kijiye', 'haan', 'acha', 'achha', 'ji', 'sir', 'mujhe'
    }
    words = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
    return len(words.intersection(hindi_keywords)) >= 2

def _play_audio_file(file_path: str):
    """Play an audio file using pygame mixer."""
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
    except Exception as e:
        console.print(f"[dim]Audio playback error: {e}[/dim]")

def _speak_hindi_neural(clean_text: str) -> bool:
    """Uses Edge-TTS Neural Indian voice (hi-IN-MadhurNeural) with gTTS fallback for natural Hindi."""
    try:
        audio_file = "jarvis_hindi_speech.mp3"
        async def _gen():
            communicate = edge_tts.Communicate(clean_text, "hi-IN-MadhurNeural", rate="+5%")
            await communicate.save(audio_file)
        asyncio.run(_gen())
        _play_audio_file(audio_file)
        return True
    except Exception:
        try:
            from gtts import gTTS
            audio_file = "jarvis_hindi_speech.mp3"
            tts = gTTS(clean_text, lang='hi')
            tts.save(audio_file)
            _play_audio_file(audio_file)
            return True
        except Exception as e:
            console.print(f"[dim]Hindi speech error: {e}[/dim]")
            return False

def _speak_builtin(clean_text: str):
    """Fallback: use Windows built-in TTS (pyttsx3)."""
    if _pyttsx3_engine:
        try:
            _pyttsx3_engine.say(clean_text)
            _pyttsx3_engine.runAndWait()
        except Exception as e:
            console.print(f"[dim]Built-in voice error: {e}[/dim]")

def speak(text):
    """
    Intelligent Bilingual Speech:
    - Hindi / Hinglish -> Microsoft Neural Indian Voice (hi-IN-MadhurNeural / gTTS) for 100% authentic pronunciation.
    - English -> ElevenLabs Ultra-Realistic Voice (Roger) with fallback.
    """
    clean_text = clean_text_for_speech(text)
    if not clean_text:
        return

    # 1. If text is Hindi or Hinglish, speak using authentic Indian neural voice
    if is_hindi_or_hinglish(clean_text):
        if _speak_hindi_neural(clean_text):
            return

    # 2. For English, use ElevenLabs
    if _speak_elevenlabs(clean_text):
        return

    # 3. Fallbacks if ElevenLabs is unavailable or quota is exceeded
    if not _speak_hindi_neural(clean_text):
        _speak_builtin(clean_text)


def listen_for_voice():
    """Listens continuously until speech is detected. Uses Google Speech API with offline Whisper fallback."""
    with sr.Microphone() as source:
        console.print("\n[bold green]🎤 JARVIS is Listening... (Speak now)[/bold green]")
        # Fast ambient noise calibration for instant listening
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=15)
            console.print("[dim]⏳ Processing speech...[/dim]")

            # Primary: Google Speech Recognition (Fast & supports English/Hindi/Hinglish)
            try:
                text = recognizer.recognize_google(audio)
            except (sr.RequestError, Exception):
                # Fallback: Whisper AI (Runs completely offline on your RTX 4050)
                console.print("[dim]Offline detected, processing with Whisper AI...[/dim]")
                text = recognizer.recognize_whisper(audio, model="base")

            console.print(f"\n[bold cyan]🗣️ You:[/bold cyan] {text}")
            return text
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            console.print(f"[dim]Audio processing error: {e}[/dim]")
            return ""

# ---------------------------------------------------------------------------
# MAIN JARVIS LOGIC
# ---------------------------------------------------------------------------
class Jarvis:
    def __init__(self):
        # Load memory
        memory_context = ""
        if os.path.exists("memory.txt"):
            with open("memory.txt", "r", encoding="utf-8") as f:
                facts = f.read().strip()
                if facts:
                    memory_context = f"\n\nHere are things you have learned and MUST remember about the user:\n{facts}"

        sys_prompt = (
            "You are JARVIS, an advanced, highly conversational personal AI assistant for your user.\n"
            "Languages: You speak fluent English, natural Hindi, and conversational Hinglish. "
            "When replying in Hindi or Hinglish, speak in natural, polite Indian phrasing "
            "(e.g., 'Ji sir, main abhi screen analyze kar raha hoon.', 'Main option click kar raha hoon.'). "
            "Never produce robotic, broken, or weird repetitive phrases.\n"
            "Capabilities & Real-Time Device Orders:\n"
            "- Live Screen Analysis: If the user asks to see, look at, check, read, or analyze what is currently on their screen, "
            "or asks about an open window, website, chart, or error, call 'analyze_screen(query)'.\n"
            "- Click Options on Device: When the user orders you to click any option, button, menu, link, or tab on their device "
            "(e.g. 'click Settings', 'click Submit', 'click Next', 'click File', 'click Save'), immediately call 'click_option(target_name)'.\n"
            "- Mouse & Coordinates: To click specific coordinates or right-click, call 'click_screen(x, y, button, clicks)'.\n"
            "- Keyboard Keys & Shortcuts: To press keys (Enter, Escape, Space, Tab, Backspace, Ctrl+W, Alt+F4, etc.), call 'press_keyboard_key(key)'.\n"
            "- Scrolling: To scroll up or down on the screen or active window, call 'scroll_screen(direction, amount)'.\n"
            "- PowerPoint: If the user asks to create or make a presentation on any topic (e.g. Big Bang), "
            "call 'create_presentation(topic)'.\n"
            "- Apps: To open any app or website, call 'open_application(app_name)'.\n"
            "- Files: To find any file or document on the computer, call 'search_computer_files(query)'. To open a file, call 'open_file(file_path)'.\n"
            "- Memory: Autonomously call 'remember_fact' whenever you learn personal user preferences.\n"
            "User's home directory is C:\\Users\\loq. Keep answers concise, polite, natural, and direct."
            + memory_context
        )

        self.messages = [
            {"role": "system", "content": sys_prompt}
        ]
        console.print(Panel(f"[bold cyan]J.A.R.V.I.S. Initialized (Voice & Memory Mode)[/bold cyan]\nPowered by {MODEL}.", border_style="cyan"))
        speak("System online. Main aapki kya madad kar sakta hoon?")

    def _needs_tools(self, prompt: str) -> bool:
        """Lightweight keyword check. Only enable tools when truly needed."""
        action_words = [
            # live screen & clicking actions
            "screen", "look", "see", "click", "tap", "press", "button", "option", "scroll",
            "down", "up", "enter", "escape", "tab", "dekho", "dikhao", "padho", "padh",
            "kaha", "daba", "dabao", "right click", "double click", "active", "window",
            # presentation ops
            "presentation", "powerpoint", "ppt", "slide", "slides", "topic",
            # file/folder ops
            "folder", "file", "create", "mkdir", "desktop", "documents",
            "find", "locate", "search", "where", "read", "khol", "kholo", "banao", "dhundo",
            "pdf", "doc", "docx", "show me",
            # apps/web
            "open", "launch", "google", "youtube", "instagram",
            "browse", "website", "internet",
            # system
            "cpu", "ram", "battery", "stats", "command", "terminal", "run",
            # typing
            "type", "write this",
            # memory
            "remember", "forget", "my name", "i am", "i'm", "i work",
            "i like", "i hate", "i prefer", "mera", "meri", "mujhe",
        ]
        p = prompt.lower()
        return any(w in p for w in action_words)

    def process_prompt(self, user_prompt: str):
        self.messages.append({"role": "user", "content": user_prompt})

        all_tools = [
            search_the_web,
            run_terminal_command,
            analyze_screen,
            click_option,
            click_screen,
            press_keyboard_key,
            scroll_screen,
            create_presentation,
            search_computer_files,
            open_file,
            create_folder,
            open_application,
            get_system_stats,
            type_on_keyboard,
            remember_fact
        ]

        # Only give tools to the model when the prompt actually warrants it.
        # This prevents the model from hallucinating tool calls on simple greetings.
        tools = all_tools if self._needs_tools(user_prompt) else []

        with console.status("[bold yellow]JARVIS is thinking..."):
            try:
                response = ollama.chat(
                    model=MODEL,
                    messages=self.messages,
                    tools=tools if tools else None
                )
            except Exception as e:
                console.print(f"[bold red]Ollama Error: {e}[/bold red]")
                self.messages.pop()
                return

        message = response.get('message', {})
        tool_calls = message.get('tool_calls', [])
        content = message.get('content', '')

        # --- Hallucination Guard ---
        # Catch any remaining cases where the model writes raw JSON in its text.
        if content and ('"name"' in content and ('"parameters"' in content or '"arguments"' in content)) and not tool_calls:
            console.print("[dim italic]Hallucination detected — stripping and retrying without tools.[/dim italic]")
            clean_messages = self.messages[:-1] + [
                {"role": "user", "content": user_prompt + "\n(Reply naturally in plain text only. Do NOT output any JSON.)"}
            ]
            with console.status("[bold yellow]JARVIS is retrying..."):
                response = ollama.chat(model=MODEL, messages=clean_messages, tools=None)
            message = response.get('message', {})
            tool_calls = message.get('tool_calls', [])
            content = message.get('content', '')

        if tool_calls:
            self.messages.append(message)
            
            for tool_call in tool_calls:
                func_name = tool_call['function']['name']
                args = tool_call['function']['arguments']
                
                console.print(f"[bold magenta]=> Executing Tool: {func_name}[/bold magenta]")
                
                try:
                    func = globals()[func_name]
                    result = func(**args)
                except Exception as e:
                    result = f"Error: {e}"
                    
                self.messages.append({
                    "role": "tool",
                    "content": str(result),
                    "name": func_name
                })
            
            with console.status(f"[bold yellow]JARVIS is reading tool results..."):
                final_response = ollama.chat(
                    model=MODEL,
                    messages=self.messages
                )
                final_content = final_response['message']['content']
                self.messages.append(final_response['message'])
                
                console.print(Panel(Markdown(final_content), border_style="green"))
                speak(final_content)
                
        else:
            content = message.get('content', '')
            self.messages.append(message)
            console.print(Panel(Markdown(content), border_style="blue"))
            speak(content)

def main():
    jarvis = Jarvis()
    console.print("[dim]💡 Tip: Say [bold]'change voice'[/bold] or [bold]'change jarvis voice'[/bold] to pick a new voice![/dim]")
    try:
        while True:
            # Fully Hands-Free Voice Loop
            user_input = listen_for_voice()

            if not user_input:
                continue

            # --- Special Commands ---
            lower = user_input.lower()

            if lower in ['exit', 'quit', 'goodbye', 'stop listening', 'bye jarvis']:
                goodbye_msg = "Shutting down JARVIS. Goodbye!"
                console.print(f"[bold red]{goodbye_msg}[/bold red]")
                speak(goodbye_msg)
                break

            if any(kw in lower for kw in ['change voice', 'change your voice', 'change jarvis voice',
                                           'switch voice', 'new voice', 'different voice', 'voice change',
                                           'apni awaaz', 'awaaz badlo', 'voice badlo']):
                speak("Sure! Opening the voice picker for you.")
                voice_picker(ELEVENLABS_API_KEY)
                speak("Done! Restart me to apply the new voice.")
                continue

            jarvis.process_prompt(user_input)
    except KeyboardInterrupt:
        console.print("[bold red]Shutting down...[/bold red]")
        sys.exit(0)

if __name__ == "__main__":
    main()
