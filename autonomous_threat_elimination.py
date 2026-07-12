"""
Autonomous Threat Elimination - Komplexná bezpečnostná vrstva
Monitorovanie, karanténa, eliminácia a alertovanie
"""

import os
import hashlib
import shutil
import ctypes
import asyncio
import logging
from datetime import datetime
from typing import Optional, List
from pathlib import Path

# Logging setup
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "security_audit.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class AutonomousThreatElimination:
    """Hlavná trieda pre elimináciu hrozieb"""
    
    SECURITY_HEADER = "[VORTEX-HEXA-SECURE:v2.1.0-CLARITY]"
    QUARANTINE_DIR = "quarantine"
    
    def __init__(self):
        self._quarantine_path = Path(self.QUARANTINE_DIR)
        self._setup_quarantine()
        self._psutil_available = self._check_psutil()
        
    def _check_psutil(self) -> bool:
        """Skontroluje či je psutil k dispozícii"""
        try:
            import psutil
            return True
        except ImportError:
            return False
    
    def _setup_quarantine(self) -> None:
        """Nastavenie karanténneho priečinka"""
        if not self._quarantine_path.exists():
            self._quarantine_path.mkdir(parents=True, exist_ok=True)
    
    def quarantine_file(self, file_path: str) -> bool:
        """Bezpečne presunie podozrivý súbor do karantény"""
        try:
            src = Path(file_path)
            if not src.exists():
                return False
                
            # Presun do karantény
            dst = self._quarantine_path / src.name
            shutil.move(str(src), str(dst))
            
            # Nastaviť práva iba na čítanie
            os.chmod(str(dst), 0o444)
            
            self._log_action("QUARANTINE", f"File quarantined: {file_path}")
            self.notify_user("QUARANTINE", file_path)
            return True
            
        except Exception as e:
            self._log_action("ERROR", f"Quarantine failed: {str(e)}")
            return False
    
    def terminate_process(self, pid: int, block_restart: bool = True) -> bool:
        """Okamžite ukončí proces a zablokuje opätovné spustenie"""
        if not self._psutil_available:
            self._log_action("ERROR", "psutil not available, cannot terminate process")
            return False
            
        try:
            import psutil
            process = psutil.Process(pid)
            
            # Získanie cesty k spustiteľnému súboru
            exe_path = process.exe()
            
            # Ukončenie procesu
            process.kill()
            
            # Zablokovanie opätovného spustenia
            if block_restart and os.path.exists(exe_path):
                blocked_path = exe_path + ".blocked"
                shutil.move(exe_path, blocked_path)
                os.chmod(blocked_path, 0o000)  # No access
            
            self._log_action("TERMINATE", f"Process terminated: PID {pid}")
            self.notify_user("TERMINATE", f"PID {pid}")
            return True
            
        except Exception as e:
            self._log_action("ERROR", f"Terminate failed: {str(e)}")
            return False
    
    def notify_user(self, threat_type: str, path: str) -> None:
        """Zobrazí varovné okno pre používateľa"""
        try:
            message = f"[VORTEX-HEXA-SECURE] Threat blocked!\nType: {threat_type}\nTarget: {path}"
            ctypes.windll.user32.MessageBoxW(0, message, "Security Alert", 0x30)
        except:
            pass  # Windows only
    
    def _log_action(self, action: str, details: str) -> None:
        """Zapíše akciu do logu"""
        timestamp = datetime.now().isoformat()
        log_entry = f"{self.SECURITY_HEADER} | {timestamp} | {action} | {details}"
        logging.info(log_entry)
    
    async def watchdog_monitor(self, watch_paths: List[str], interval: float = 1.0):
        """Asynchrónne monitorovanie súborov"""
        import time
        
        hashes = {}
        
        # Inicializácia hašov
        for path in watch_paths:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    hashes[path] = hashlib.sha256(f.read()).hexdigest()
        
        while True:
            for path in watch_paths:
                if os.path.exists(path):
                    try:
                        with open(path, 'rb') as f:
                            current_hash = hashlib.sha256(f.read()).hexdigest()
                        
                        if path in hashes and hashes[path] != current_hash:
                            self.quarantine_file(path)
                            hashes[path] = current_hash
                    except:
                        pass
            
            await asyncio.sleep(interval)
    
    async def process_monitor(self, suspicious_patterns: Optional[List[str]] = None):
        """Monitorovanie procesov"""
        if not self._psutil_available:
            self._log_action("INFO", "psutil not available, process monitoring disabled")
            return
            
        import psutil
        
        if suspicious_patterns is None:
            suspicious_patterns = ["encrypt", "ransom", "malware", "trojan"]
        
        while True:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    for pattern in suspicious_patterns:
                        if pattern in proc_name:
                            self.terminate_process(proc.info['pid'])
                            break
                except:
                    pass
            
            await asyncio.sleep(2.0)


# Standalone funkcie pre ľahké použitie
_ate_instance = AutonomousThreatElimination()


def quarantine_file(file_path: str) -> bool:
    """Quarantine file wrapper"""
    return _ate_instance.quarantine_file(file_path)


def terminate_process(pid: int) -> bool:
    """Terminate process wrapper"""
    return _ate_instance.terminate_process(pid)


def notify_user(threat_type: str, path: str) -> None:
    """Notify user wrapper"""
    _ate_instance.notify_user(threat_type, path)


__all__ = [
    'AutonomousThreatElimination',
    'quarantine_file',
    'terminate_process', 
    'notify_user',
]