"""
Langkah 5 - Menyiapkan data ringkas untuk dashboard web (docs/index.html).

Menjalankan sql/07 dan sql/08, lalu menyimpannya sebagai docs/data.js.
Dashboard membaca file ini dan menghitung ulang angka setiap kali filter diubah.
"""
import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "database" / "pengaduan.db"
OUT = ROOT / "docs" / "data.js"

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

with sqlite3.connect(DB) as con:
    kubus = pd.read_sql_query((ROOT / "sql" / "07_data_dashboard.sql").read_text(encoding="utf-8"), con)
    jam = pd.read_sql_query((ROOT / "sql" / "08_data_dashboard_jam.sql").read_text(encoding="utf-8"), con)
    sla = dict(con.execute("SELECT kategori, MAX(target_sla_jam) FROM pengaduan GROUP BY kategori").fetchall())

bulan = sorted(kubus["bulan"].unique())
unit = sorted(kubus["unit_layanan"].unique())
kategori = (kubus.groupby("kategori")["n"].sum().sort_values(ascending=False).index.tolist())
tahun = sorted(jam["tahun"].unique().tolist())

ukuran = ["n", "n_dinilai", "n_tepat", "total_durasi", "n_durasi", "n_rating", "total_rating", "n_ulang",
          "n_tepat_diikuti", "n_telat_diikuti", "n_rating_tepat", "total_rating_tepat",
          "n_rating_telat", "total_rating_telat"]
baris_kubus = [[bulan.index(r.bulan), unit.index(r.unit_layanan), kategori.index(r.kategori)]
               + [round(float(getattr(r, c)), 2) if c == "total_durasi" else int(getattr(r, c)) for c in ukuran]
               for r in kubus.itertuples()]
baris_jam = [[tahun.index(r.tahun), unit.index(r.unit_layanan), kategori.index(r.kategori),
              HARI.index(r.hari_lapor), int(r.jam_lapor), int(r.n)] for r in jam.itertuples()]

data = dict(bulan=bulan, unit=unit, kategori=kategori, tahun=tahun, hari=HARI,
            sla={k: int(v) for k, v in sla.items()}, ukuran=ukuran,
            kubus=baris_kubus, jam=baris_jam, target_persen=90)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("// Dibuat otomatis oleh scripts/05_siapkan_data_dashboard.py - jangan diedit manual.\n"
               "window.DATA_DASHBOARD = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n",
               encoding="utf-8")
print(f"{len(baris_kubus)} baris ringkas + {len(baris_jam)} baris jam -> {OUT.relative_to(ROOT)} "
      f"({OUT.stat().st_size / 1024:.0f} KB)")
