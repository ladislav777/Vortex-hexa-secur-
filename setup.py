#!/usr/bin/env python3
"""
Vortex & Hexa - Setup script pre inštaláciu
"""

from setuptools import setup, find_packages

setup(
    name="vortex_hexa",
    version="2.1.0",
    description="Secure scanning and hashing system",
    author="VortexHexa",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pycryptodome>=3.19.0",
    ],
    entry_points={
        "console_scripts": [
            "vortex-hexa=main:main",
        ],
    },
)