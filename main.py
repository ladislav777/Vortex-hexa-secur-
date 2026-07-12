#!/usr/bin/env python3
"""
Vortex & Hexa Secure - Background Service
Zero UI: Beží ako neviditeľný proces na pozadí.
Triggered UI: Iba licenčné okno (1. spustenie) a alert okno pri hrozbe.
"""

import sys
import os
import time
import threading
import ctypes
import hashlib
import json
import subprocess
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vortex.scanner import VortexScanner
from vortex.indexer import VortexIndexer
from hexa.hasher import HexaHasher
from hexa.matrix import HexaMatrix
from security import SecurityLayer, STATIC_SECURITY_HEADER, format_secure_log
from license import check_license, LicenseManager
from autonomous_threat_elimination import AutonomousThreatElimination
from privacy_auditor import PrivacyAuditor


# =====================================================================
# LICENČNÉ OKNO (zobrazí sa iba pri prvom spustení)
# =====================================================================

class LicenseWindow:
    """Jediné GUI okno - výzva na zadanie licenčného kľúča"""
    
    @staticmethod
    def show_activation_dialog() -> bool:
        """
        Zobrazí dialóg pre aktiváciu licencie.
        Vráti True ak bola licencia úspešne aktivovaná.
        """
        try:
            result = ctypes.windll.user32.MessageBoxW(
                0,
                "VORTEX & HEXA SECURE\n\n"
                "Pre aktiváciu zadajte licenčný kľúč.\n"
                "Kľúč nájdete v dokumentácii produktu.\n\n"
                "Chcete zadať licenčný kľúč teraz?",
                "Aktivácia Licencie",
                0x34  # Yes/No + Warning icon
            )
            
            if result == 6:  # Yes
                return LicenseWindow._show_key_entry_dialog()
            else:
                return False
        except Exception:
            return False
    
    @staticmethod
    def _show_key_entry_dialog() -> bool:
        """
        Zobrazí PowerShell input box pre zadanie licenčného kľúča.
        """
        try:
            ps_command = (
                '[System.Reflection.Assembly]::LoadWithPartialName("Microsoft.VisualBasic") | Out-Null; '
                '$key = [Microsoft.VisualBasic.Interaction]::InputBox('
                '"Zadajte licenčný kľúč", '
                '"Aktivácia Vortex & Hexa Secure", '
                '""); '
                'Write-Output $key'
            )
            
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True, text=True, timeout=30
            )
            
            license_key = result.stdout.strip()
            if license_key:
                return LicenseWindow._validate_and_save_key(license_key)
            
            return False
            
        except Exception as e:
            print(f"License dialog error: {e}")
            return False
    
    @staticmethod
    def _validate_and_save_key(key: str) -> bool:
        """Validácia a uloženie licenčného kľúča"""
        if len(key) < 16:
            ctypes.windll.user32.MessageBoxW(
                0,
                "Neplatný formát licenčného kľúča.\n"
                "Kľúč musí obsahovať minimálne 16 znakov.",
                "Chyba Aktivácie",
                0x10  # Error icon
            )
            return False
        
        try:
            hwid = LicenseManager().get_hwid()
            payload = {
                "hwid": hwid,
                "key_hash": hashlib.sha256(key.encode()).hexdigest(),
                "activated": datetime.now().isoformat(),
                "expires": (datetime.now() + timedelta(days=365)).isoformat(),
                "type": "licensed"
            }
            
            license_data = {
                "hwid": hwid,
                "payload": json.dumps(payload),
                "signature": hashlib.sha256(json.dumps(payload).encode()).hexdigest()[:64],
                "expires": payload["expires"]
            }
            
            with open("license.vhl", 'w') as f:
                json.dump(license_data, f, indent=2)
            
            ctypes.windll.user32.MessageBoxW(
                0,
                "Licencia bola úspešne aktivovaná!\n\n"
                "Aplikácia bude teraz bežať na pozadí.",
                "Aktivácia Dokončená",
                0x40  # Info icon
            )
            return True
            
        except Exception as e:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Chyba pri ukladaní licencie: {e}",
                "Chyba Aktivácie",
                0x10
            )
            return False


# =====================================================================
# VÝSTRAŽNÉ OKNO (zobrazí sa iba pri detekcii hrozby)
# =====================================================================

class ThreatAlertWindow:
    """Výstražné okno s obrázkom na pozadí - jediné UI za behu"""
    
    BACKGROUND_IMAGE = "alert_background.png"
    
    @staticmethod
    def show_alert(threat_type: str, target: str, details: str = "") -> bool:
        """
        Zobrazí výstražné okno s informáciami o hrozbe.
        Vráti True ak používateľ potvrdí elimináciu.
        """
        try:
            image_path = ThreatAlertWindow.BACKGROUND_IMAGE
            if os.path.exists(image_path):
                return ThreatAlertWindow._show_image_alert(threat_type, target, details, image_path)
            else:
                return ThreatAlertWindow._show_text_alert(threat_type, target, details)
        except Exception:
            return ThreatAlertWindow._show_text_alert(threat_type, target, details)
    
    @staticmethod
    def _show_text_alert(threat_type: str, target: str, details: str) -> bool:
        """Textová verzia alertu (fallback)"""
        message = (
            "\u26a0 VORTEX & HEXA SECURE - HROZBA ZACHYTEN\u00c1 \u26a0\n\n"
            f"Typ: {threat_type}\n"
            f"Cie\u013e: {target}\n"
        )
        if details:
            message += f"Detail: {details}\n"
        message += "\nChcete vykona\u0165 elimina\u010dn\u00fd protokol?"
        
        result = ctypes.windll.user32.MessageBoxW(
            0,
            message,
            "VORTEX SECURITY ALERT",
            0x34  # Yes/No + Warning
        )
        return result == 6
    
    @staticmethod
    def _show_image_alert(threat_type: str, target: str, details: str, image_path: str) -> bool:
        """
        Zobrazí alert s obrázkom na pozadí cez PowerShell.
        """
        try:
            ps_script = (
                'Add-Type -AssemblyName System.Windows.Forms; '
                'Add-Type -AssemblyName System.Drawing; '
                '$form = New-Object System.Windows.Forms.Form; '
                '$form.Text = "VORTEX SECURITY ALERT"; '
                '$form.Size = New-Object System.Drawing.Size(600,400); '
                '$form.StartPosition = "CenterScreen"; '
                '$form.TopMost = $true; '
                '$form.FormBorderStyle = "FixedDialog"; '
                '$form.ControlBox = $false; '
                'if (Test-Path "' + image_path + '") { '
                '  $img = [System.Drawing.Image]::FromFile("' + image_path + '"); '
                '  $form.BackgroundImage = $img; '
                '  $form.BackgroundImageLayout = "Stretch"; '
                '}; '
                '$label = New-Object System.Windows.Forms.Label; '
                '$label.Text = "\u26a0 HROZBA ZACHYTEN\u00c1 \u26a0`n`n'
                'Typ: ' + threat_type + '`n'
                'Cie\u013e: ' + target + '`n'
                + details + '"; '
                '$label.Location = New-Object System.Drawing.Point(20,20); '
                '$label.Size = New-Object System.Drawing.Size(560,200); '
                '$label.BackColor = [System.Drawing.Color]::FromArgb(180, 0, 0, 0); '
                '$label.ForeColor = [System.Drawing.Color]::Red; '
                '$label.Font = New-Object System.Drawing.Font("Consolas", 12, [System.Drawing.FontStyle]::Bold); '
                '$form.Controls.Add($label); '
                '$btnEliminate = New-Object System.Windows.Forms.Button; '
                '$btnEliminate.Text = "ELIMINOVA\u0164 HROZBU"; '
                '$btnEliminate.Location = New-Object System.Drawing.Point(150,250); '
                '$btnEliminate.Size = New-Object System.Drawing.Size(300,50); '
                '$btnEliminate.BackColor = [System.Drawing.Color]::DarkRed; '
                '$btnEliminate.ForeColor = [System.Drawing.Color]::White; '
                '$btnEliminate.Font = New-Object System.Drawing.Font("Consolas", 14, [System.Drawing.FontStyle]::Bold); '
                '$btnEliminate.Add_Click({ $form.Tag = "eliminate"; $form.Close() }); '
                '$form.Controls.Add($btnEliminate); '
                '$btnIgnore = New-Object System.Windows.Forms.Button; '
                '$btnIgnore.Text = "IGNOROVA\u0164"; '
                '$btnIgnore.Location = New-Object System.Drawing.Point(200,320); '
                '$btnIgnore.Size = New-Object System.Drawing.Size(200,40); '
                '$btnIgnore.BackColor = [System.Drawing.Color]::FromArgb(50,50,50); '
                '$btnIgnore.ForeColor = [System.Drawing.Color]::Gray; '
                '$btnIgnore.Font = New-Object System.Drawing.Font("Consolas", 10); '
                '$btnIgnore.Add_Click({ $form.Tag = "ignore"; $form.Close() }); '
                '$form.Controls.Add($btnIgnore); '
                '$form.ShowDialog(); '
                '$form.Dispose(); '
                'Write-Output $form.Tag'
            )
            
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
                capture_output=True, text=True, timeout=60
            )
            
            return 'eliminate' in result.stdout.lower()
            
        except Exception as e:
            return ThreatAlertWindow._show_text_alert(threat_type, target, details)


# =====================================================================
# BACKGROUND SERVICE
# =====================================================================

class VortexBackgroundService:
    """Hlavná služba bežiaca na pozadí - Zero UI"""
    
    def __init__(self):
        self.running = False
        self.security = SecurityLayer()
        self.ate = AutonomousThreatElimination()
        self.license_manager = LicenseManager()
        self.scanner = VortexScanner(".")
        self.hasher = HexaHasher()
        self.matrix = HexaMatrix()
        
        self.SCAN_INTERVAL = 300       # 5 minút
        self.PRIVACY_INTERVAL = 3600   # 1 hodina
        self.THREAT_INTERVAL = 60      # 1 minúta
        
    def start(self):
        """Spustenie služby na pozadí"""
        self.running = True
        self.security.initialize()
        self.hasher.init_salt("vortex_hexa_secure")
        
        print(f"{STATIC_SECURITY_HEADER} | Background service started")
        print(f"{STATIC_SECURITY_HEADER} | HWID: {self.license_manager.get_hwid()}")
        print(f"{STATIC_SECURITY_HEADER} | PID: {os.getpid()}")
        
        threads = [
            threading.Thread(target=self._scan_loop, daemon=True),
            threading.Thread(target=self._privacy_loop, daemon=True),
            threading.Thread(target=self._threat_loop, daemon=True),
        ]
        
        for t in threads:
            t.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Zastavenie služby"""
        self.running = False
        print(f"{STATIC_SECURITY_HEADER} | Background service stopped")
    
    def _scan_loop(self):
        """Pravidelné skenovanie súborov"""
        while self.running:
            try:
                results = self.scanner.index_files()
                if results.get("total", 0) > 0:
                    print(f"{STATIC_SECURITY_HEADER} | Scan: {results['total']} files indexed")
                    
                    indexer = VortexIndexer(self.scanner)
                    indexer.build_index()
                    
                    values = [1, 2, 3, 4, 5, 6, 7, 8]
                    self.matrix.process_chain(values)
                    
            except Exception as e:
                print(f"{STATIC_SECURITY_HEADER} | Scan error: {e}")
            
            for _ in range(self.SCAN_INTERVAL):
                if not self.running:
                    return
                time.sleep(1)
    
    def _privacy_loop(self):
        """Pravidelný Privacy Audit"""
        while self.running:
            try:
                auditor = PrivacyAuditor()
                auditor.generate_privacy_report()
                
                risky_apps = auditor.get_risky_apps()
                if risky_apps:
                    print(f"{STATIC_SECURITY_HEADER} | Privacy: {len(risky_apps)} risky apps detected")
                    
                    for app in risky_apps:
                        should_eliminate = ThreatAlertWindow.show_alert(
                            threat_type="PRIVACY RISK",
                            target=app['name'],
                            details=f"Nebezpečné povolenia: {', '.join(app['dangerous_permissions'])}"
                        )
                        
                        if should_eliminate:
                            print(f"{STATIC_SECURITY_HEADER} | Privacy: User approved action for {app['name']}")
                
            except Exception as e:
                print(f"{STATIC_SECURITY_HEADER} | Privacy audit error: {e}")
            
            for _ in range(self.PRIVACY_INTERVAL):
                if not self.running:
                    return
                time.sleep(1)
    
    def _threat_loop(self):
        """Pravidelná kontrola hrozieb"""
        while self.running:
            try:
                import psutil
                suspicious_patterns = ["encrypt", "ransom", "malware", "trojan", "keylog", "spy", "rat", "backdoor"]
                
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        proc_name = proc.info['name'].lower()
                        for pattern in suspicious_patterns:
                            if pattern in proc_name:
                                print(f"{STATIC_SECURITY_HEADER} | Threat detected: {proc.info['name']} (PID: {proc.info['pid']})")
                                
                                should_eliminate = ThreatAlertWindow.show_alert(
                                    threat_type="MALICIOUS PROCESS",
                                    target=proc.info['name'],
                                    details=f"PID: {proc.info['pid']}\nVzor: {pattern}"
                                )
                                
                                if should_eliminate:
                                    self.ate.terminate_process(proc.info['pid'])
                                    print(f"{STATIC_SECURITY_HEADER} | Process terminated: {proc.info['pid']}")
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
            except ImportError:
                pass
            except Exception as e:
                print(f"{STATIC_SECURITY_HEADER} | Threat check error: {e}")
            
            for _ in range(self.THREAT_INTERVAL):
                if not self.running:
                    return
                time.sleep(1)


# =====================================================================
# MAIN - VSTUPNÝ BOD
# =====================================================================

def main() -> int:
    """Hlavný vstupný bod - Zero UI background service"""
    
    # 1. Skrytie konzolového okna (ak je spustené ako .exe)
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass
    
    # 2. Kontrola licencie
    if not os.path.exists("license.vhl"):
        print(f"{STATIC_SECURITY_HEADER} | First run - activation required")
        
        if not LicenseWindow.show_activation_dialog():
            print(f"{STATIC_SECURITY_HEADER} | Activation cancelled. Exiting.")
            return 1
    
    # 3. Validácia existujúcej licencie
    if not check_license():
        print(f"{STATIC_SECURITY_HEADER} | License validation failed. Exiting.")
        return 1
    
    # 4. Spustenie background service
    print(f"{STATIC_SECURITY_HEADER} | Vortex & Hexa Secure starting...")
    
    service = VortexBackgroundService()
    service.start()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())