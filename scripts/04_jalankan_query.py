"""
Langkah 4 - Menjalankan query analisis (sql/01-06) dan menyimpan hasilnya.

Keluaran: outputs/hasil_query/<nama_query>.csv
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "database" / "pengaduan.db"
OUT = ROOT / "outputs" / "hasil_query"
OUT.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(DB) as con:
    for f in sorted((ROOT / "sql").glob("0[1-6]_*.sql")):
        hasil = pd.read_sql_query(f.read_text(encoding="utf-8"), con)
        hasil.to_csv(OUT / f"{f.stem}.csv", index=False)
        print(f"\n=== {f.stem} ===")
        print(hasil.to_string(index=False))
