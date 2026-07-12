#!/usr/bin/env python3
"""
Key Generator for Vortex & Hexa Licenses
Pre Ladislava - generuje licenčné súbory pre kamarátov
"""

import os
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional


# Embedded private key pre podpis (v reálnom systéme by bol offline)
# Toto je demo key - v produkcii by bol skutočný privátny kľúč
PRIVATE_KEY_SEED = "vortex_hexa_license_key_2024"


def generate_license_key(hwid: str, days_valid: int = 365, custom_payload: Optional[str] = None) -> dict:
    """
    Generuje licenčný súbor pre dané HWID
    
    Args:
        hwid: Hardvérové ID kamaráta
        days_valid: Počet dní platnosti (default: 365)
        custom_payload: Voliteľný payload
    
    Returns:
        License dictionary
    """
    
    # Vypočítať expiráciu
    expires = (datetime.now() + timedelta(days=days_valid)).isoformat()
    
    # Payload
    payload = custom_payload or f"vortex_hexa_license_{hwid[:8]}"
    
    # Digitálny podpis (zjednodušený)
    signature = hashlib.sha256(
        f"{PRIVATE_KEY_SEED}{hwid}{payload}".encode()
    ).hexdigest()[:64]
    
    license_data = {
        "hwid": hwid,
        "payload": payload,
        "signature": signature,
        "expires": expires,
        "version": "2.1.0",
        "product": "VortexHexa"
    }
    
    return license_data


def save_license(license_data: dict, output_file: str = "license.vhl") -> None:
    """Uloží licenčný súbor"""
    with open(output_file, 'w') as f:
        json.dump(license_data, f, indent=2)
    print(f"License saved to: {output_file}")


def main():
    """Interaktívny generátor kľúčov"""
    print("=" * 50)
    print("Vortex & Hexa - License Generator")
    print("=" * 50)
    
    # Získanie HWID od používateľa
    hwid = input("Enter friend's HWID: ").strip()
    
    if not hwid:
        print("Error: HWID is required!")
        return
    
    # Voliteľná platnosť
    days_input = input("Days valid (default 365): ").strip()
    days = int(days_input) if days_input.isdigit() else 365
    
    # Voliteľný payload
    payload = input("Custom payload (optional): ").strip() or None
    
    # Generovanie
    license_data = generate_license_key(hwid, days, payload)
    
    # Uloženie
    output_file = input("Output filename (default license.vhl): ").strip() or "license.vhl"
    save_license(license_data, output_file)
    
    print("\nLicense Details:")
    print(json.dumps(license_data, indent=2))


if __name__ == "__main__":
    main()