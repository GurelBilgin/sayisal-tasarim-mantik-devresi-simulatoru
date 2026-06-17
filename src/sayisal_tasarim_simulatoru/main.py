"""Uygulama giriş noktası.

Bu dosya hem paket olarak (`python -m sayisal_tasarim_simulatoru.main`)
hem de PyInstaller tarafından doğrudan script olarak çalıştırıldığında kullanılabilir.
"""

from __future__ import annotations

import sys
from pathlib import Path


if __package__ in (None, ""):
    # PyInstaller veya doğrudan dosya çalıştırma durumunda `src` klasörünü
    # Python arama yoluna ekleyerek mutlak importların çalışmasını sağlar.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sayisal_tasarim_simulatoru.gui import run_app


def main() -> None:
    """Tkinter arayüzünü başlatır."""
    run_app()


if __name__ == "__main__":
    main()