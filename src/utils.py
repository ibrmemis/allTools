import sys
import subprocess

def check_and_install(package, import_name=None):
    """Gerekli Python paketlerinin kurulu olup olmadığını denetler, yoksa kurar."""
    import importlib
    name = import_name or package
    try:
        importlib.import_module(name)
    except ImportError:
        # Kurulum yap
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

import re

def natural_sort_key(text):
    """
    Sayısal sıralama (natural sorting) için anahtar fonksiyonu.
    '1.jpg', '2.jpg', '10.jpg' şeklinde sıralar (alfabetik değil).
    """
    def atoi(t):
        return int(t) if t.isdigit() else t.lower()
    
    return [atoi(c) for c in re.split(r'(\d+)', text)]
