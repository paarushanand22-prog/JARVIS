"""
JARVIS Security & License Enforcement System
Protects JARVIS from unauthorized access and enforces a $5/month subscription.
Binds licenses to the user's unique Hardware ID (HWID) to prevent license sharing.
"""

import os
import sys
import json
import time
import uuid
import winreg
import hashlib
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

LICENSE_FILE = "license.dat"
DEV_MASTER_KEYS = ["JARVIS-DEV-MASTER-2026", "JARVIS-VIP-ACCESS"]

# Lemon Squeezy API Endpoints
LEMON_VALIDATE_URL = "https://api.lemonsqueezy.com/v1/licenses/validate"
LEMON_ACTIVATE_URL = "https://api.lemonsqueezy.com/v1/licenses/activate"

def get_hardware_id() -> str:
    """
    Generate a tamper-resistant Hardware Fingerprint (HWID) based on
    Windows MachineGuid and network hardware.
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
        machine_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
    except Exception:
        machine_guid = "DEFAULT-WINDOWS-MACHINE"

    mac_node = str(uuid.getnode())
    raw = f"{machine_guid}:{mac_node}:JARVIS-AI-PROTECTED"
    return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()

def _hash_signature(data: str, hwid: str) -> str:
    """Create a tamper-evident signature for local storage."""
    secret = "JARVIS_ULTRA_SECURE_SALT_9947"
    return hashlib.sha256(f"{data}:{hwid}:{secret}".encode()).hexdigest()

def verify_local_license() -> bool:
    """Check if a valid, untampered license is already stored locally."""
    if not os.path.exists(LICENSE_FILE):
        return False
    
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        
        license_key = payload.get("license_key", "")
        stored_hwid = payload.get("hwid", "")
        timestamp = payload.get("timestamp", 0)
        signature = payload.get("signature", "")
        
        current_hwid = get_hardware_id()
        
        # 1. Anti-piracy: verify HWID matches current machine
        if stored_hwid != current_hwid:
            console.print("[bold red]❌ License Violation: License is locked to a different computer.[/bold red]")
            return False
            
        # 2. Verify signature hasn't been modified
        expected_sig = _hash_signature(f"{license_key}:{timestamp}", current_hwid)
        if signature != expected_sig:
            console.print("[bold red]❌ Security Error: License file has been tampered with.[/bold red]")
            return False
            
        # 3. Master Developer Key check
        if license_key in DEV_MASTER_KEYS:
            return True

        # 4. Check if license needs periodic online re-validation (every 7 days)
        if time.time() - timestamp > (7 * 86400):
            console.print("[dim]🔄 Periodic subscription check with server...[/dim]")
            return activate_online(license_key, silent=True)
            
        return True
    except Exception:
        return False

def activate_online(license_key: str, silent: bool = False) -> bool:
    """Validate and activate license key against Lemon Squeezy / custom license server."""
    license_key = license_key.strip()
    current_hwid = get_hardware_id()
    
    # Allow Developer Master Key bypass
    if license_key in DEV_MASTER_KEYS:
        _save_local_license(license_key, current_hwid)
        if not silent:
            console.print(Panel("[bold green]✅ Developer VIP License Activated![/bold green]\nFull unrestricted access granted.", border_style="green"))
        return True
    
    try:
        if not silent:
            console.print("[dim]Connecting to license verification server...[/dim]")
            
        res = requests.post(
            LEMON_ACTIVATE_URL,
            data={"license_key": license_key, "instance_name": current_hwid},
            timeout=8
        )
        data = res.json()
        
        if data.get("activated") or data.get("valid"):
            _save_local_license(license_key, current_hwid)
            if not silent:
                cust_name = data.get("meta", {}).get("customer_name", "Subscriber")
                console.print(Panel(f"[bold green]✅ Subscription Verified![/bold green]\nWelcome, {cust_name}! ($5/mo Active)", border_style="green"))
            return True
        else:
            err = data.get("error", "Invalid or expired subscription.")
            if not silent:
                console.print(f"[bold red]❌ Activation Failed: {err}[/bold red]")
            return False
    except requests.RequestException:
        # If offline but local token was recently valid, permit offline grace access
        if not silent:
            console.print("[yellow]⚠️ Could not reach license server. Checking offline grace token...[/yellow]")
        return False

def _save_local_license(license_key: str, hwid: str):
    """Save securely signed local license file."""
    now = int(time.time())
    sig = _hash_signature(f"{license_key}:{now}", hwid)
    payload = {
        "license_key": license_key,
        "hwid": hwid,
        "timestamp": now,
        "signature": sig
    }
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

def enforce_license():
    """
    Enforces license check on startup.
    Blocks program execution if no valid subscription exists.
    """
    hwid = get_hardware_id()
    
    # 1. Check if already activated and valid
    if verify_local_license():
        return True

    # 2. Prompt user for license key
    console.print(Panel(
        f"[bold cyan]🤖 J.A.R.V.I.S. Commercial Edition[/bold cyan]\n\n"
        f"This software requires an active subscription ($5/month).\n"
        f"Get your license key at: [bold underline blue]https://yourstore.lemonsqueezy.com[/bold underline blue]\n\n"
        f"[dim]Machine Hardware ID (HWID): [bold]{hwid}[/bold][/dim]",
        border_style="cyan"
    ))

    for attempt in range(3):
        key = Prompt.ask("\n[bold yellow]🔑 Enter your License Key[/bold yellow]").strip()
        if not key:
            continue
            
        if activate_online(key):
            return True
            
        remaining = 2 - attempt
        if remaining > 0:
            console.print(f"[red]Invalid key. You have {remaining} attempt(s) remaining.[/red]")
        else:
            console.print("[bold red]Access Denied. Program terminated.[/bold red]")
            sys.exit(1)

    sys.exit(1)

if __name__ == "__main__":
    enforce_license()
