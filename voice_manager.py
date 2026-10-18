"""
Voice Manager for JARVIS
Fetches available ElevenLabs voices and updates config.py
"""
import requests
from rich.console import Console
from rich.table import Table

console = Console()

def get_elevenlabs_voices(api_key: str) -> list:
    """Fetch all available voices from ElevenLabs."""
    try:
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": api_key},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("voices", [])
        else:
            return []
    except Exception:
        return []

def update_voice_in_config(voice_id: str, voice_name: str):
    """Update the ELEVENLABS_VOICE_ID in config.py."""
    import re
    # Always resolve config.py relative to this file's directory
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        r'ELEVENLABS_VOICE_ID\s*=\s*".*?"',
        f'ELEVENLABS_VOICE_ID = "{voice_id}"',
        content
    )
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)
    console.print(f"[bold green]✅ Voice saved: {voice_name}[/bold green]")

def voice_picker(api_key: str):
    """Interactive voice picker — shows a table of all available voices."""
    console.print("\n[bold cyan]Fetching your available voices from ElevenLabs...[/bold cyan]")
    voices = get_elevenlabs_voices(api_key)

    if not voices:
        console.print("[bold red]Could not fetch voices. Check your API key and internet connection.[/bold red]")
        return

    table = Table(title="🎙️ Available ElevenLabs Voices", border_style="cyan", show_lines=True)
    table.add_column("No.", style="bold yellow", width=5)
    table.add_column("Name", style="bold white", width=20)
    table.add_column("Category", style="dim", width=15)
    table.add_column("Gender", style="dim", width=10)
    table.add_column("Voice ID", style="dim cyan", width=25)

    for i, voice in enumerate(voices, start=1):
        labels = voice.get("labels", {})
        table.add_row(
            str(i),
            voice.get("name", "Unknown"),
            voice.get("category", "-"),
            labels.get("gender", "-"),
            voice.get("voice_id", "-")
        )

    console.print(table)

    choice = console.input("\n[bold cyan]Enter the number of the voice you want (or press Enter to cancel): [/bold cyan]").strip()
    if not choice:
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(voices):
            selected = voices[idx]
            update_voice_in_config(selected["voice_id"], selected["name"])
        else:
            console.print("[red]Invalid choice.[/red]")
    except ValueError:
        console.print("[red]Please enter a valid number.[/red]")

if __name__ == "__main__":
    # Run standalone to pick a voice
    try:
        from config import ELEVENLABS_API_KEY
        if not ELEVENLABS_API_KEY:
            console.print("[bold red]No API key found in config.py![/bold red]")
        else:
            voice_picker(ELEVENLABS_API_KEY)
    except ImportError:
        console.print("[bold red]config.py not found![/bold red]")
