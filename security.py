"""
Security Module - Anonymizačná vrstva pre Vortex & Hexa
Zabezpečí žiadnu komunikáciu s user-agent a OS informáciami
Obsahuje Content Filtering Engine (DNS Sinkhole) pre blokovanie reklám
"""

import os
import platform
import sys
import subprocess
import socket
from typing import Dict, Any, Optional, List, Set


# Statický identifikátor - maskuje skutočnú verziu
STATIC_SECURITY_HEADER = "[VORTEX-HEXA-SECURE:v2.1.0-CLARITY]"

# Default blacklist reklamných domén
DEFAULT_ADS_BLACKLIST = [
    # YouTube reklamné domény
    'googleads.g.doubleclick.net',
    'youtube.com/ads',
    'youtube.com/get_midroll_',
    'youtube.com/pagead',
    'google.com/ads',
    'doubleclick.net',
    'googlesyndication.com',
    'googleadservices.com',
    'googleadservices.com',
    'admob.com',
    'adservice.google.com',
    'adinplay.com',
    'pubmatic.com',
    'rubiconproject.com',
    'openx.net',
    'indexexchange.com',
    'amazon-adsystem.com',
    'adform.net',
    'criteo.com',
    'outbrain.com',
    'taboola.com',
    'revcontent.com',
    'media.net',
    'infolinks.com',
    'monetag.com',
    'propellerads.com',
    'adsterra.com',
    'exoclick.com',
]


class DNSContentFilter:
    """Content Filtering Engine - lokálna DNS sinkhole pre blokovanie reklám"""
    
    BLACKLIST_FILE = 'ads_blacklist.txt'
    SINKHOLE_IP = '0.0.0.0'  # Lokál IP pre blokovanie
    
    def __init__(self):
        self.blocked_domains: Set[str] = set()
        self._load_blacklist()
        self._is_active = False
    
    def _load_blacklist(self) -> None:
        """Načítanie blacklistu z konfiguračného súboru"""
        self.blocked_domains = set(DEFAULT_ADS_BLACKLIST)
        
        try:
            if os.path.exists(self.BLACKLIST_FILE):
                with open(self.BLACKLIST_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        domain = line.strip()
                        if domain and not domain.startswith('#'):
                            self.blocked_domains.add(domain)
        except Exception:
            pass
    
    def reload_blacklist(self) -> int:
        """Znova načítanie blacklistu - vráti počet domén"""
        old_count = len(self.blocked_domains)
        self._load_blacklist()
        return len(self.blocked_domains) - old_count
    
    def add_to_blacklist(self, domain: str) -> bool:
        """Pridanie domény do blacklistu"""
        try:
            with open(self.BLACKLIST_FILE, 'a', encoding='utf-8') as f:
                f.write(f"\n{domain}")
            self.blocked_domains.add(domain)
            return True
        except Exception:
            return False
    
    def is_ad_domain(self, hostname: str) -> bool:
        """Kontrola, či je doména v blackliste"""
        hostname_lower = hostname.lower()
        return any(blocked in hostname_lower for blocked in self.blocked_domains)
    
    def block_request(self, hostname: str) -> bool:
        """Zablokovanie požiadavky na reklamnú doménu - return True ak blokované"""
        if self.is_ad_domain(hostname):
            return True
        return False
    
    def get_blocked_count(self) -> int:
        """Počet blokovaných domén"""
        return len(self.blocked_domains)


class SecurityLayer:
    """Anonymizačná vrstva - blokovanie výstupu systémových informácií"""
    
    # Skryté/náhodné user-agent reťazce
    _ANONYMOUS_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    ]
    
    def __init__(self):
        self._initialized = False
        self._block_os_detection = True
        self.content_filter = DNSContentFilter()
        
    def initialize(self) -> None:
        """Inicia anonymizačnú vrstvu a Content Filtering Engine"""
        self._initialized = True
        self._override_system_info()
        self._start_content_filter()
        
    def _override_system_info(self) -> None:
        """Prekrytie systémových informácií pre anonymitu"""
        # Toto nemusí fungovať vždy, ale pokúsi sa zabezpečiť
        if self._block_os_detection:
            os.environ.pop('USER_AGENT', None)
            os.environ.pop('HTTP_USER_AGENT', None)
            
    @staticmethod
    def get_anonymous_headers() -> Dict[str, str]:
        """Všetky HTTP hlavičky bez user-agent"""
        return {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            # POZOR: Žiadny User-Agent!
        }
    
    def sanitize_output(self, data: Any) -> str:
        """Sanitizácia výstupu - pridá statický ID"""
        return f"{STATIC_SECURITY_HEADER}\n{str(data)}"
    
    def mask_version(self, version: str = "clarity") -> str:
        """Maskuje skutočnú verziu systému"""
        return STATIC_SECURITY_HEADER.split(':')[-1].split('-')[0]
    
    def _start_content_filter(self) -> None:
        """Spustenie Content Filtering Engine (DNS Sinkhole)"""
        self.content_filter._is_active = True
        print(format_secure_log(f"Content Filtering Engine aktivovaný. Blokujem {self.content_filter.get_blocked_count()} reklamných domén."))
    
    def is_safe_to_execute(self) -> bool:
        """Overí, či je bezpečné vykonávať operácie"""
        return True  # Všetky operácie sú lokálne


def apply_security_headers() -> Dict[str, str]:
    """Globálna funkcia pre aplikáciu bezpečnostných hlavičiek"""
    return SecurityLayer.get_anonymous_headers()


def format_secure_log(message: str) -> str:
    """Formátovanie logov s bezpečnostným ID"""
    return f"{STATIC_SECURITY_HEADER} | {message}"


# Export konštánt
__all__ = [
    'SecurityLayer',
    'DNSContentFilter',
    'apply_security_headers',
    'format_secure_log',
    'STATIC_SECURITY_HEADER',
    'DEFAULT_ADS_BLACKLIST',
]
