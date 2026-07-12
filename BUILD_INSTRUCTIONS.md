# Vortex & Hexa - Build Instructions

## Hotové Build Komponenty

### 1. Windows Executable (Black Box)
- **Súbor**: `C:\Users\jpjpj\Desktop\dist\vortex_hexa_secure.exe`
- **Parametre**: `--onefile --noconsole --strip`
- **Stav**: ✅ Hotové

### 2. Obfuscated Python (PyArmor)
- **Súbor**: `C:\Users\jpjpj\Desktop\vortex_hexa\dist\obfuscated\main.py`
- **Runtime**: `dist\obfuscated\pyarmor_runtime_000000\pyarmor_runtime.pyd`
- **Stav**: ✅ Hotové

### 3. Licenčný Systém
- **Hardware ID**: `hardware_id.py` - zobrazí HWID pre registráciu
- **Key Generator**: `key_generator.py` - pre Ladislava na generovanie licencií
- **License Manager**: `license.py` - validácia a self-destruct

## License Workflow

1. Používateľ spustí `hardware_id.py` a získá svoje HWID
2. HWID pošle Ladislavovi
3. Ladislav spustí `key_generator.py` a vygeneruje `license.vhl`
4. Používateľ uloží `license.vhl` do priečinky s aplikáciou
5. Aplikácia overí licenciu pri štarte

## Build Príkazy

### Windows (.exe)
```bash
pyinstaller --onefile --noconsole --strip --name vortex_hexa_secure main.py
```

### Android (APK)
```bash
cd buildspec
buildozer android debug
```

## Bezpečnostné Vlastnosti Implementované

1. **Žiadny user-agent** - `security.py` má `get_anonymous_headers()` bez user-agent
2. **Žiadne OS info** - všetky operácie sú lokálne, žiadna exfiltrace
3. **Maskovaná verzia** - statický identifikátor `[VORTEX-HEXA-SECURE:v2.1.0-CLARITY]`

## Architektúra Projektu

```
vortex_hexa/
├── vortex/                    # Vortex Scanner modul
│   ├── __init__.py
│   ├── scanner.py             # Prescanová logika
│   └── indexer.py             # Indexácia výsledkov
├── hexa/                      # Hexa Hash modul
│   ├── __init__.py
│   ├── hasher.py              # Kryptografické hashovanie
│   └── matrix.py              # 64-bitové matice
├── buildspec/                 # Build konfigurácie
│   ├── buildozer.spec        # Android APK
│   ├── pyinstaller.spec      # Windows EXE
│   └── build_secure.bat      # Automatický build script
├── dist/                      # Výstupné súbory
│   ├── vortex_hexa_secure.exe # Windows executable
│   └── obfuscated/            # Zašifrovaný kód
├── security.py                # Anonymizačná vrstva
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
└── setup.py                   # Setup script
```

## Využitie

Projekt je pripravený na bezpečnú distribúciu. Všetky komponenty sú oddelené od job_hunter projektu.