# Vortex & Hexa - Bezpečná Distribučná Architektúra

## Prehľad

Vortex & Hexa je systém pre bezpečné skenovanie a hashovanie s nasledujúcimi komponentami:

- **Vortex** - prescanová logika pre analýzu a indexáciu
- **Hexa** - kryptografické hashovanie s 64-bitovými operáciami

## Architektúra

```
vortex_hexa/
├── vortex/
│   ├── __init__.py
│   ├── scanner.py      # Vortex core scanning logic
│   └── indexer.py      # Indexácia výsledkov
├── hexa/
│   ├── __init__.py
│   ├── hasher.py       # Hexa hash core
│   └── matrix.py       # 64-bitová matica operácií
├── main.py             # Entry point
├── security.py         # Anonymizačná vrstva
└── buildspec/
    ├── buildozer.spec   # Android build
    └── pyinstaller.spec # Windows build
```

## Komponenty

### Vortex Scanner
- Prescanová analýza súborov a adresárov
- Indexácia obsahu do interného formátu
- Bezpečnostná izolácia (read-only)

### Hexa Hasher
- Kryptografické hashovanie (SHA-256 + custom)
- 64-bitové operácie na maticiach
- Verzijný systém s maskovaním

## Bezpečnostné Vlastnosti

1. **Žiadny user-agent** - všetky HTTP requesty anonymné
2. **Žiadne OS info** - systémové informácie blokované
3. **Lokálne operácie** - žiadra exfiltrace dát
4. **Maskovaná verzia** - statický identifikátor namiesto skutočnej verzie