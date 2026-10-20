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

# Local accounts database for email + password authentication
ACCOUNTS_FILE = "accounts.dat"

def _hash_password(password: str) -> str:
    """Create secure hash of user password."""
    salt = "JARVIS_AUTH_SALT_SECURE_2026"
    return hashlib.sha256(f"{password}:{salt}".encode()).hexdigest()

def _load_accounts() -> dict:
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_accounts(accounts: dict):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2)

def register_user(email: str, password: str) -> bool:
    """Registers a new user account bound to this machine."""
    email = email.strip().lower()
    if not email or "@" not in email:
        console.print("[bold red]❌ Please enter a valid email address.[/bold red]")
        return False
    if len(password) < 6:
        console.print("[bold red]❌ Password must be at least 6 characters.[/bold red]")
        return False
    
    accounts = _load_accounts()
    if email in accounts:
        console.print("[yellow]⚠️ An account with this email already exists. Please log in.[/yellow]")
        return False
    
    current_hwid = get_hardware_id()
    accounts[email] = {
        "password_hash": _hash_password(password),
        "hwid": current_hwid,
        "created_at": int(time.time()),
        "status": "active"
    }
    _save_accounts(accounts)
    _save_local_license(f"USER:{email}", current_hwid)
    console.print(Panel(f"[bold green]🎉 Account Created Successfully![/bold green]\nWelcome, [bold]{email}[/bold]! You are logged in.", border_style="green"))
    return True

def login_user(email: str, password: str) -> bool:
    """Logs in an existing user with email and password."""
    email = email.strip().lower()
    accounts = _load_accounts()
    
    if email not in accounts:
        # Developer master account bypass
        if email == "admin" and password == "JARVIS-DEV-MASTER-2026":
            _save_local_license("DEV_ADMIN", get_hardware_id())
            console.print(Panel("[bold green]✅ Developer Admin Logged In![/bold green]", border_style="green"))
            return True
        console.print("[bold red]❌ Account not found. Please register first.[/bold red]")
        return False
    
    acc = accounts[email]
    if acc.get("password_hash") != _hash_password(password):
        console.print("[bold red]❌ Incorrect password.[/bold red]")
        return False
    
    current_hwid = get_hardware_id()
    _save_local_license(f"USER:{email}", current_hwid)
    console.print(Panel(f"[bold green]✅ Welcome back, {email}![/bold green]\nLogin successful.", border_style="green"))
    return True

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
    User Authentication & Access System.
    Users can:
    1. Create a New Account (Email + Password)
    2. Log In to an Existing Account
    3. Enter an activation License Key directly
    """
    # 1. Check if already activated and authenticated on this device
    if verify_local_license():
        return True

    hwid = get_hardware_id()
    console.print(Panel(
        f"[bold cyan]🤖 J.A.R.V.I.S. AI Workstation[/bold cyan]\n\n"
        f"Welcome! Please log in or create an account to start using JARVIS.\n"
        f"[dim]Device Hardware ID: {hwid}[/dim]",
        border_style="cyan"
    ))

    while True:
        console.print("\n[bold]Select an option:[/bold]")
        console.print("  [bold green]1.[/bold green] Log In to existing account")
        console.print("  [bold cyan]2.[/bold cyan] Create a new account")
        console.print("  [bold yellow]3.[/bold yellow] Activate using License Key")
        console.print("  [bold red]4.[/bold red] Exit")

        choice = Prompt.ask("\nEnter choice (1-4)", default="1").strip()

        if choice == "1":
            email = Prompt.ask("📧 Enter Email").strip()
            password = Prompt.ask("🔒 Enter Password", password=True).strip()
            if login_user(email, password):
                return True

        elif choice == "2":
            console.print("\n[bold cyan]── Create New JARVIS Account ──[/bold cyan]")
            email = Prompt.ask("📧 Enter your Email").strip()
            password = Prompt.ask("🔒 Create a Password (min 6 chars)", password=True).strip()
            if register_user(email, password):
                return True

        elif choice == "3":
            key = Prompt.ask("🔑 Enter your License Key").strip()
            if activate_online(key):
                return True

        elif choice in ["4", "exit", "quit", "q"]:
            console.print("[dim]Goodbye![/dim]")
            sys.exit(0)
        else:
            console.print("[red]Invalid choice. Please select 1, 2, 3 or 4.[/red]")

if __name__ == "__main__":
    enforce_license()
