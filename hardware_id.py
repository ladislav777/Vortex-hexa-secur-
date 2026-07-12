#!/usr/bin/env python3
"""
Hardware ID Generator for License Registration
Bezpečný spôsob ako získať HWID pre licenciu
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from license import HardwareID, LicenseManager


def main():
    """Zobrazí používateľove HWID pre registráciu"""
    hwid = HardwareID.generate_hwid()
    lm = LicenseManager()
    
    print("=" * 50)
    print("Vortex & Hexa - Hardware ID Registration")
    print("=" * 50)
    print(f"\nYour Hardware ID: {hwid}")
    print("\nSend this to Ladislav to get your license file.")
    print("Save the received license.vhl in the application folder.\n")


if __name__ == "__main__":
    main()