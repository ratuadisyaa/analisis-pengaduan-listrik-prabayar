"""
Langkah 3 - Memuat data bersih ke database SQLite.

SQLite dipilih karena tidak perlu instalasi server. File database bisa dibuka
dengan DB Browser for SQLite (gratis) untuk latihan query.

Keluaran: database/pengaduan.db (tabel: pengaduan)
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "pengaduan_bersih.csv"
DB = ROOT / "database" / "pengaduan.db"

SKEMA = """
CREATE TABLE pengaduan (
    id_tiket                 TEXT PRIMARY KEY,
    id_pelanggan             TEXT NOT NULL,
    waktu_lapor              TEXT NOT NULL,   -- format 'YYYY-MM-DD HH:MM:SS'
    waktu_selesai            TEXT,            -- kosong jika belum/tidak selesai
    tahun                    INTEGER,
    bulan                    TEXT,            -- 'YYYY-MM'
    hari_lapor               TEXT,
    jam_lapor                INTEGER,
    unit_layanan             TEXT,
    kategori                 TEXT,
    kanal                    TEXT,
    daya_va                  INTEGER,
    status                   TEXT,            -- Selesai / Dalam Proses / Dibatalkan
    durasi_jam               REAL,            -- kosong jika tidak valid
    durasi_valid             INTEGER,
    target_sla_jam           INTEGER,
    tepat_waktu              INTEGER,         -- 1 = selesai <= target SLA, 0 = terlambat
    rating_kepuasan          INTEGER,         -- 1-5, kosong jika tidak mengisi survei
    pengaduan_ulang          INTEGER,         -- 1 = pernah lapor kategori sama <= 30 hari sebelumnya
    diikuti_pengaduan_ulang  INTEGER          -- 1 = lapor lagi <= 30 hari setelah tiket ini selesai
);
CREATE INDEX idx_bulan ON pengaduan(bulan);
CREATE INDEX idx_unit_kategori ON pengaduan(unit_layanan, kategori);
CREATE INDEX idx_pelanggan ON pengaduan(id_pelanggan, kategori, waktu_lapor);
"""

df = pd.read_csv(CSV, dtype={"daya_va": "Int64", "durasi_valid": "Int64", "tepat_waktu": "Int64",
                             "rating_kepuasan": "Int64", "diikuti_pengaduan_ulang": "Int64"})
DB.parent.mkdir(parents=True, exist_ok=True)
DB.unlink(missing_ok=True)
with sqlite3.connect(DB) as con:
    con.executescript(SKEMA)
    df.to_sql("pengaduan", con, if_exists="append", index=False)
    n = con.execute("SELECT COUNT(*) FROM pengaduan").fetchone()[0]
print(f"{n:,} baris dimuat ke {DB.relative_to(ROOT)}")
