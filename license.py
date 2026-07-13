class LicenseManager:
    """Správa licenčného mechanizmu"""
    
    def self_destruct(self) -> None:
        """Sebedestrukcia - mazanie dočasných súborov"""
        import shutil
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        vortex_temp = os.path.join(temp_dir, "vortex_hexa")
        
        if os.path.exists(vortex_temp):
            shutil.rmtree(vortex_temp)
        
        # Smazat súbor protokolov
        log_file = "vortex_hexa.log"
        if os.path.exists(log_file):
            os.remove(log_file)
            
        print(f"{self.SECURITY_HEADER} | Sebezničenie zahájené")
