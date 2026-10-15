"""
Menjalankan seluruh alur proyek secara berurutan.

    python jalankan_semua.py            # pakai data mentah yang sudah ada
    python jalankan_semua.py --ulang    # buat ulang data simulasi dari awal juga

Data mentah sudah disertakan di data/raw/, jadi langkah 01 dilewati secara
bawaan. Membuat ulang data bisa menghasilkan angka yang sedikit berbeda dari
README jika versi NumPy berbeda.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
langkah = sorted((ROOT / "scripts").glob("0*.py"))
if "--ulang" not in sys.argv and (ROOT / "data" / "raw" / "pengaduan_raw.csv").exists():
    langkah = [p for p in langkah if not p.name.startswith("01_")]
for p in langkah:
    print(f"\n>>> {p.name}")
    subprocess.run([sys.executable, str(p)], check=True)
print("\nSelesai. Buka docs/index.html di browser untuk melihat dashboard.")
