#!/usr/bin/env python3
"""
Vortex & Hexa Secure - Android verzia
Zero UI background service pre Android s Kivy UI
"""

import sys
import os
import time
import threading
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vortex.scanner import VortexScanner
from vortex.indexer import VortexIndexer
from hexa.hasher import HexaHasher
from hexa.matrix import HexaMatrix
from security import SecurityLayer, STATIC_SECURITY_HEADER, format_secure_log
from license import check_license, LicenseManager
from autonomous_threat_elimination import AutonomousThreatElimination
from privacy_auditor import PrivacyAuditor
from ad_blocker import AdBlocker

KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 10
    
    Label:
        text: 'Vortex & Hexa Secure'
        font_size: 24
        size_hint_y: 0.3
        
    Label:
        id: status_label
        text: 'Service running...'
        font_size: 14
        size_hint_y: 0.4
        
    Button:
        text: 'Stop Service'
        size_hint_y: 0.3
        on_press: app.stop_service()
'''


class VortexAndroidService:
    """Android background service"""
    
    def __init__(self):
        self.running = False
        self.security = SecurityLayer()
        self.ate = AutonomousThreatElimination()
        self.license_manager = LicenseManager()
        self.scanner = VortexScanner("/sdcard")
        self.hasher = HexaHasher()
        self.matrix = HexaMatrix()
        
        self.SCAN_INTERVAL = 300
        self.PRIVACY_INTERVAL = 3600
        self.THREAT_INTERVAL = 60
        
    def start(self):
        self.running = True
        self.security.initialize()
        self.hasher.init_salt("vortex_hexa_secure")
        
        print(f"{STATIC_SECURITY_HEADER} | Android service started")
        print(f"{STATIC_SECURITY_HEADER} | HWID: {self.license_manager.get_hwid()}")
        
        # Spusti ad blocker
        self.ad_blocker = AdBlocker()
        self.ad_blocker.start()
        
        threads = [
            threading.Thread(target=self._scan_loop, daemon=True),
            threading.Thread(target=self._privacy_loop, daemon=True),
            threading.Thread(target=self._threat_loop, daemon=True),
            threading.Thread(target=self._adblock_loop, daemon=True),
        ]
        
        for t in threads:
            t.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        self.running = False
        print(f"{STATIC_SECURITY_HEADER} | Android service stopped")
    
    def _scan_loop(self):
        while self.running:
            try:
                results = self.scanner.index_files()
                if results.get("total", 0) > 0:
                    print(f"{STATIC_SECURITY_HEADER} | Scan: {results['total']} files")
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
        while self.running:
            try:
                auditor = PrivacyAuditor()
                auditor.generate_privacy_report()
                risky_apps = auditor.get_risky_apps()
                if risky_apps:
                    print(f"{STATIC_SECURITY_HEADER} | Privacy: {len(risky_apps)} risky apps")
                    for app in risky_apps:
                        print(f"  - {app['name']}: {', '.join(app['dangerous_permissions'])}")
            except Exception as e:
                print(f"{STATIC_SECURITY_HEADER} | Privacy error: {e}")
            
            for _ in range(self.PRIVACY_INTERVAL):
                if not self.running:
                    return
                time.sleep(1)
    
    def _threat_loop(self):
        while self.running:
            try:
                import psutil
                suspicious = ["encrypt", "ransom", "malware", "trojan", "keylog", "spy"]
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        for pattern in suspicious:
                            if pattern in proc_name:
                                print(f"{STATIC_SECURITY_HEADER} | Threat: {proc.info['name']} (PID: {proc.info['pid']})")
                                self.ate.terminate_process(proc.info['pid'])
                                break
                    except:
                        pass
            except ImportError:
                pass
            except Exception as e:
                print(f"{STATIC_SECURITY_HEADER} | Threat error: {e}")
            
            for _ in range(self.THREAT_INTERVAL):
                if not self.running:
                    return
                time.sleep(1)
    
    def _adblock_loop(self):
        while self.running:
            try:
                # Každých 60 sekúnd obnov blokovanie (pre prípad zmeny hosts)
                if hasattr(self, 'ad_blocker'):
                    blocked, failed = self.ad_blocker.block_all() if hasattr(self.ad_blocker, 'block_all') else (0, 0)
                    if blocked > 0:
                        print(f"{STATIC_SECURITY_HEADER} | AdBlock: {blocked} domén blokovaných")
            except Exception as e:
                print(f"{STATIC_SECURITY_HEADER} | AdBlock error: {e}")
            
            for _ in range(60):
                if not self.running:
                    return
                time.sleep(1)


class VortexHexaApp(App):
    """Hlavní Kivy aplikace"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = None
        
    def build(self):
        return Builder.load_string(KV)
    
    def on_start(self):
        # Inicializace služby
        if not os.path.exists("license.vhl"):
            lm = LicenseManager()
            lm.auto_activate()
        
        if check_license():
            self.service = VortexAndroidService()
            self.service.start()
    
    def stop_service(self):
        if self.service:
            self.service.stop()
        self.stop()


if __name__ == "__main__":
    VortexHexaApp().run()
