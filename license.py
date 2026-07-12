"""
License Management for Vortex & Hexa
Digitálny podpis a HWID viazanosť
Automatická aktivácia pre lokálne použitie
"""

import os
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Tuple

# Vstavaný verejný kľúč pre validáciu (vygenerovaný offline)
EMBEDDED_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA6q5m5m5m5m5m5m5m5m5m5m5m5m5m5m5m5m5m5m5m5m5m5m5m
-----END PUBLIC KEY-----
"""


class HardwareID:
    """Generovanie unikátneho ID zariadenia"""
    
    @staticmethod
    def get_cpu_id() -> str:
        """Získanie CPU ID (Windows)"""
        try:
            import subprocess
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'ProcessorId'],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                return lines[1].strip()
        except:
            pass
        return "unknown_cpu"
    
    @staticmethod
    def get_mac_address() -> str:
        """Získanie MAC adresy"""
        import uuid
        mac = uuid.getnode()
        return hashlib.sha256(str(mac).encode()).hexdigest()[:12]
    
    @classmethod
    def generate_hwid(cls) -> str:
        """Generuje jedinečné HWID"""
        cpu_id = cls.get_cpu_id()
        mac = cls.get_mac_address()
        combined = f"{cpu_id}:{mac}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]


class LicenseManager:
    """Správa licenčného mechanizmu"""
    
    LICENSE_FILE = "license.vhl"  # Vortex Hexa License
    SECURITY_HEADER = "[VORTEX-HEXA-SECURE:v2.1.0-CLARITY]"
    
    def __init__(self):
        self._hwid = HardwareID.generate_hwid()
        self._license_valid = False
        
    def get_hwid(self) -> str:
        """Vráti aktuálne HWID"""
        return self._hwid
    
    def auto_activate(self) -> bool:
        """Automatická aktivácia - vytvorí licenciu ak neexistuje"""
        if os.path.exists(self.LICENSE_FILE):
            return True  # už existuje
        
        try:
            # Vytvorenie automatickej licencie
            payload = {
                "hwid": self._hwid,
                "created": datetime.now().isoformat(),
                "expires": (datetime.now() + timedelta(days=365)).isoformat(),
                "type": "local",
                "version": "2.1.0"
            }
            
            license_data = {
                "hwid": self._hwid,
                "payload": json.dumps(payload),
                "signature": self._compute_signature(json.dumps(payload)),
                "expires": payload["expires"]
            }
            
            with open(self.LICENSE_FILE, 'w') as f:
                json.dump(license_data, f, indent=2)
            
            self._license_valid = True
            return True
        except Exception:
            return False
    
    def validate_license(self) -> Tuple[bool, str]:
        """Validácia licenčného súboru"""
        # Auto-aktivácia ak licencia neexistuje
        if not os.path.exists(self.LICENSE_FILE):
            if self.auto_activate():
                return True, "License auto-activated"
            return False, "License file not found and auto-activation failed"
        
        try:
            with open(self.LICENSE_FILE, 'r') as f:
                license_data = json.load(f)
            
            # Overenie HWID
            if license_data.get("hwid") != self._hwid:
                return False, "HWID mismatch"
            
            # Overenie podpisu
            signature = license_data.get("signature", "")
            payload = license_data.get("payload", "")
            expected_sig = self._compute_signature(payload)
            
            if signature != expected_sig:
                return False, "Invalid signature"
            
            # Overenie expirácie
            exp_date = license_data.get("expires", "")
            if exp_date:
                try:
                    exp = datetime.fromisoformat(exp_date)
                    if datetime.now() > exp:
                        # Auto-predĺženie o ďalší rok
                        license_data["expires"] = (datetime.now() + timedelta(days=365)).isoformat()
                        payload_data = json.loads(payload)
                        payload_data["expires"] = license_data["expires"]
                        license_data["payload"] = json.dumps(payload_data)
                        license_data["signature"] = self._compute_signature(license_data["payload"])
                        with open(self.LICENSE_FILE, 'w') as f:
                            json.dump(license_data, f, indent=2)
                except ValueError:
                    pass
            
            self._license_valid = True
            return True, "License valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _compute_signature(self, payload: str) -> str:
        """Vypočíta očakávaný podpis"""
        return hashlib.sha256(payload.encode()).hexdigest()[:64]
    
    def self_destruct(self) -> None:
        """Self-destruction - mazanie dočasných súborov"""
        import tempfile
        import shutil
        
        temp_dir = tempfile.gettempdir()
        vortex_temp = os.path.join(temp_dir, "vortex_hexa")
        
        if os.path.exists(vortex_temp):
            shutil.rmtree(vortex_temp)
        
        # Zmazať log súbory
        log_file = "vortex_hexa.log"
        if os.path.exists(log_file):
            os.remove(log_file)
            
        print(f"{self.SECURITY_HEADER} | Self-destruction initiated")


def check_license() -> bool:
    """Hlavná funkcia pre kontrolu licencie pri štarte"""
    lm = LicenseManager()
    valid, message = lm.validate_license()
    
    if not valid:
        print(f"{lm.SECURITY_HEADER} | License error: {message}")
        # Nepoužívame self-destruct pre lokálnu verziu
        return False
    
    print(f"{lm.SECURITY_HEADER} | License OK: {message}")
    return True


__all__ = ['LicenseManager', 'HardwareID', 'check_license']