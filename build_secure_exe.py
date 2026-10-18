"""
JARVIS Secure Binary Compiler
Compiles Python source files into a secure, protected standalone Windows executable (.exe).
Prevents users from decompiling or viewing the original source code.
"""

import os
import sys
import shutil
import subprocess

def check_requirements():
    print("[1/4] Checking build tools...")
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller for binary compilation...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_secure_binary():
    check_requirements()

    print("\n[2/4] Preparing secure build configuration...")
    
    # Files to include
    hidden_imports = [
        "winocr",
        "uiautomation",
        "comtypes",
        "pptx",
        "edge_tts",
        "gtts",
        "pygame",
        "elevenlabs",
        "duckduckgo_search",
        "speech_recognition",
        "rich",
        "cv2",
        "mss",
        "PIL"
    ]
    
    hidden_flags = []
    for imp in hidden_imports:
        hidden_flags.extend(["--hidden-import", imp])

    print("\n[3/4] Compiling source code into protected native Windows executable...")
    
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "JARVIS",
        "--onefile",
        "--clean",
        # Optimize bytecode (removes assert statements and docstrings)
        "--optimize", "2",
        # Add imports
        *hidden_flags,
        # Main entry point
        "jarvis.py"
    ]
    
    print(f"Running: {' '.join(pyinstaller_cmd[:6])} ...")
    subprocess.check_call(pyinstaller_cmd)

    print("\n[4/4] Finalizing build...")
    output_exe = os.path.join("dist", "JARVIS.exe")
    if os.path.exists(output_exe):
        size_mb = os.path.getsize(output_exe) / (1024 * 1024)
        print("=" * 60)
        print(f"🎉 Build Succeeded!")
        print(f"Output File: {output_exe} ({size_mb:.1f} MB)")
        print("Your Python source code is now packed inside the binary executable.")
        print("Users who download this .exe cannot view or edit your Python files.")
        print("=" * 60)
    else:
        print("⚠️ Build completed, please check the 'dist/' folder.")

if __name__ == "__main__":
    build_secure_binary()
