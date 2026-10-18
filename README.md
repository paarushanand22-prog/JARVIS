# 🤖 J.A.R.V.I.S.
### Just A Rather Very Intelligent System

A fully local, voice-controlled AI assistant powered by **Ollama**, **OpenAI Whisper**, and **ElevenLabs**. JARVIS listens to your voice, thinks using locally-running LLMs, and speaks back to you in ultra-realistic audio — all running on your own PC. No cloud AI fees. No data leaks.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🧠 **Local AI Brain** | Powered by `llama3.2` via Ollama. Runs 100% offline. |
| 👁️ **Live Screen Analysis** | Real-time screen inspection using Windows OCR + Ollama `llava` vision AI. Reads active windows, text, charts, and errors. |
| 🖱️ **Device Control & Clicking** | Clicks any button, menu, tab, or option on your device upon voice order (`click Settings`, `click Submit`, etc.). |
| 📊 **PowerPoint Presentation Creator** | Generates complete, formatted multi-slide PowerPoint presentations on any topic and launches them in PowerPoint. |
| 🔍 **Full Computer File Search** | Rapidly searches across all drives (`Desktop`, `Documents`, `D:`, `E:`) to find and open any document or file. |
| 🎤 **Ultra-Smooth Speech Recognition** | Instant response with Google Web Speech API and offline Whisper AI GPU fallback. |
| 🔊 **Intelligent Bilingual Speech** | Authentic Microsoft Neural Indian Voice (`hi-IN-MadhurNeural`) for natural Hindi/Hinglish + ElevenLabs for English. |
| 🌐 **Internet Access** | Live web search via DuckDuckGo for real-time answers. |
| 💻 **PC Control** | Opens apps, creates folders, runs terminal commands, controls the keyboard & mouse. |
| 🧠 **Persistent Memory** | Automatically learns facts about you from your conversations and remembers them across sessions. |
| 🎙️ **Voice Switcher** | Change JARVIS's voice on-the-fly just by saying *"change voice"*. |
| 🛡️ **Safety Sandbox** | Destructive terminal commands (`rmdir`, `del`, `format`) are automatically blocked. |
| ⚡ **Smart Tool Routing** | Tools are only activated when needed, preventing the AI from hallucinating on simple greetings. |

---

## 🖥️ System Requirements

This project is **optimized for your hardware**:

| Component | Spec |
|---|---|
| CPU | Intel Core i5-13450HX |
| GPU | NVIDIA RTX 4050 (6GB VRAM) — runs Whisper + llama3.2 |
| RAM | 16GB |
| OS | Windows 11 |

> **Note:** `llama3.2` (3B params, ~2GB VRAM) was specifically chosen to fit entirely inside the 6GB VRAM, ensuring **instant responses** with no model swapping.

---

## 📁 Project Structure

```
JARVIS/
├── jarvis.py          # 🚀 Main entry point — run this to start JARVIS
├── system_tools.py    # 🛠️  All tools: web search, folder creation, app launcher, etc.
├── voice_manager.py   # 🎙️  Interactive ElevenLabs voice picker
├── config.py          # ⚙️  Your API keys and voice settings (DO NOT share publicly)
├── memory.txt         # 🧠  Auto-generated: JARVIS's long-term memory about you
├── requirements.txt   # 📦  All Python dependencies
└── setup.bat          # 🔧  One-click setup script
```

---

## 🚀 Installation

### Step 1 — Install Ollama
Download and install **[Ollama for Windows](https://ollama.com/download/windows)**.

### Step 2 — Pull the AI Model
Open a terminal and run:
```cmd
ollama pull llama3.2
```

### Step 3 — Install Python Dependencies
```cmd
python -m pip install -r requirements.txt
```

### Step 4 — Configure API Keys
Open `config.py` and add your **ElevenLabs API key**:
```python
ELEVENLABS_API_KEY = "your_key_here"
```
Get a free key from **[elevenlabs.io](https://elevenlabs.io)** → Profile → API Keys.

> If you leave the key blank, JARVIS will use your **Windows built-in voice** automatically.

### Step 5 — Run JARVIS
```cmd
python jarvis.py
```
JARVIS will speak *"System online. Main aapki kya madad kar sakta hoon?"* and start listening!

---

## 🗣️ How to Use

JARVIS is **100% hands-free**. Just speak naturally after it says it's listening. Here are examples:

### 💬 General Chat
> *"Hello Jarvis"* → Replies conversationally

### 🌐 Web Search
> *"Jarvis, search what is the price of iPhone 16 in India"*
> *"Aaj ki news kya hai?"*

### 💻 Computer Control
> *"Open Chrome"*
> *"Open Instagram"* *(opens in browser)*
> *"Create a folder on my Desktop called Projects"*
> *"What is my CPU usage?"*

### 🎙️ Change Voice
> *"Change voice"* / *"Change your voice"* / *"Awaaz badlo"*

### 🔴 Shutdown
> *"Goodbye"* / *"Bye Jarvis"* / *"Exit"*

---

## 🧠 How the Memory System Works

JARVIS automatically extracts and saves personal facts from your conversations into **`memory.txt`**.

For example, if you say:
> *"I'm a software engineer and I love dark mode"*

JARVIS will silently save:
```
User is a software engineer.
User loves dark mode.
```

On the **next startup**, these facts are loaded directly into JARVIS's brain — so he always remembers who you are.

---

## 🛡️ Safety & Privacy

- ✅ All AI processing runs **locally on your PC** — your conversations are never sent to any AI cloud server.
- ✅ Web searches use **DuckDuckGo** (no tracking, no login required).
- ✅ Destructive terminal commands (`rmdir`, `del`, `format`, `diskpart`) are **permanently blocked**.
- ⚠️ Keep `config.py` **private** — never upload it to GitHub or share it publicly as it contains your API key.

---

## 🎙️ Voice Architecture

```
Primary  →  ElevenLabs (eleven_multilingual_v2)  — Ultra-realistic, supports Hindi/English/Hinglish
    ↓ (if quota exhausted or key missing)
Fallback →  Windows Built-in TTS (pyttsx3)       — Offline, always available
```

JARVIS **automatically switches** to the fallback voice if:
- No API key is configured
- Your monthly ElevenLabs quota runs out
- There is a network error

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `python -m pip install -r requirements.txt` |
| `ollama: connection refused` | Make sure the Ollama app is running in the background |
| JARVIS speaks Spanish / gibberish | Background noise — it's a Whisper hallucination. Just speak again. |
| ElevenLabs voice not found | JARVIS auto-fixes this on startup and saves the correct voice to `config.py` |
| Folder created in wrong location | Specify the full location: *"Create a folder on my Desktop called X"* |
| Slow response | Make sure Ollama is running and `llama3.2` model is pulled |

---

## 📜 License

This project is for personal use. Built with ❤️ by you, powered by open-source AI.
