"""
Vortex Hexa Secure - Ad Blocker (DNS filter)
Blokuje reklamné a trackovacie domény na úrovni DNS.
Podporuje Windows (hosts súbor) a Android (DNS redirect cez VPN).
"""

import os
import sys
import threading
import time
import socket

# Zoznam reklamných domén na blokovanie
AD_BLOCK_LIST = [
    # YouTube reklamy
    "googlevideo.com",
    "youtube.com",
    "doubleclick.net",
    "googlesyndication.com",
    "googleadservices.com",
    "google-analytics.com",
    "adservice.google.com",
    "static.doubleclick.net",
    "imasdk.googleapis.com",
    # Všeobecné reklamy
    "adsystem.com",
    "adnxs.com",
    "rubiconproject.com",
    "pubmatic.com",
    "criteo.com",
    "scorecardresearch.com",
    "moatads.com",
    "adsrvr.org",
    "taboola.com",
    "outbrain.com",
    "popads.net",
    "propellerads.com",
    "mgid.com",
    "revcontent.com",
    "adblade.com",
    "bidtellect.com",
    "yahoo.com",
    "admob.com",
    "chartboost.com",
    "appnexus.com",
    "openx.net",
    "casalemedia.com",
    "spotx.tv",
    "freewheel.tv",
    "adcolony.com",
    "vungle.com",
    "unityads.unity3d.com",
    "tapjoy.com",
    "ironsrc.com",
    "applovin.com",
    "mintegral.com",
    "fyber.com",
    "inmobi.com",
    "startapp.com",
    "mobvista.com",
]

WINDOWS_HOSTS = r"C:\Windows\System32\drivers\etc\hosts"
ANDROID_HOSTS = "/system/etc/hosts"
REDIRECT_IP = "127.0.0.1"


def get_platform():
    if sys.platform.startswith("win"):
        return "windows"
    elif sys.platform.startswith("linux"):
        return "android"
    return "unknown"


def is_blocked(domain):
    """Kontrola či doména je v zozname na blokovanie"""
    domain = domain.lower().strip()
    for blocked in AD_BLOCK_LIST:
        if domain == blocked or domain.endswith("." + blocked):
            return True
    return False


def block_domain_windows(domain):
    """Prida doménu do Windows hosts súboru"""
    try:
        if not os.path.exists(WINDOWS_HOSTS):
            return False
        with open(WINDOWS_HOSTS, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        entry = f"{REDIRECT_IP} {domain}"
        if entry in content:
            return True  # Už blokované
        with open(WINDOWS_HOSTS, "a", encoding="utf-8") as f:
            f.write(f"\n{entry}\n")
        return True
    except PermissionError:
        return False
    except Exception:
        return False


def block_domain_android(domain):
    """Prida doménu do Android hosts súboru (vyžaduje root)"""
    try:
        with open(ANDROID_HOSTS, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        entry = f"{REDIRECT_IP} {domain}"
        if entry in content:
            return True
        with open(ANDROID_HOSTS, "a", encoding="utf-8") as f:
            f.write(f"\n{entry}\n")
        return True
    except Exception:
        return False


def block_all():
    """Blokuje všetky reklamné domény podľa platformy"""
    platform = get_platform()
    blocked = 0
    failed = 0
    for domain in AD_BLOCK_LIST:
        if platform == "windows":
            if block_domain_windows(domain):
                blocked += 1
            else:
                failed += 1
        elif platform == "android":
            if block_domain_android(domain):
                blocked += 1
            else:
                failed += 1
    return blocked, failed


def resolve_domain(domain):
    """Skontroluje DNS resolúciu - ak je doména blokovaná, vráti None"""
    if is_blocked(domain):
        return None
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return None


class AdBlocker:
    """Spúšťa ad blocking v backgrounde"""

    def __init__(self):
        self.running = False
        self.platform = get_platform()

    def start(self):
        self.running = True
        blocked, failed = block_all()
        print(f"[ADBLOCK] Blokované domény: {blocked}, zlyhané: {failed}")
        if failed > 0:
            print(f"[ADBLOCK] Upozornenie: {failed} domén vyžaduje admin/root práva")
        # Na Androide by tu bežala VPN služba pre DNS filtering
        # Na Windowsi stačí hosts súbor

    def stop(self):
        self.running = False
        print(f"[ADBLOCK] Ad blocker zastavený")


# Test
if __name__ == "__main__":
    blocker = AdBlocker()
    blocker.start()

    # Test
    test_domains = ["google.com", "doubleclick.net", "youtube.com", "googlevideo.com"]
    for d in test_domains:
        ip = resolve_domain(d)
        status = "BLOKOVANÉ" if ip is None else f"OK ({ip})"
        print(f"{d}: {status}")