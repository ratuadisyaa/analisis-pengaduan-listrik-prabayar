"""
Langkah 2 - Membersihkan data mentah.

Masalah yang ditangani (semuanya umum ditemui di data operasional):
  1. Baris ganda (tiket terkirim dua kali)
  2. Penulisan nama unit dan kategori yang tidak seragam
  3. Dua format tanggal berbeda di kolom waktu_lapor
  4. Daya tercatat sebagai "900" dan "900 VA", sebagian kosong
  5. Kanal pengaduan kosong
  6. Waktu selesai lebih awal dari waktu lapor (salah input)

Setiap perbaikan dicatat jumlahnya ke outputs/laporan_pembersihan.md agar
prosesnya bisa diperiksa orang lain.

Keluaran: data/processed/pengaduan_bersih.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "pengaduan_raw.csv"
OUT = ROOT / "data" / "processed" / "pengaduan_bersih.csv"
LAPORAN = ROOT / "outputs" / "laporan_pembersihan.md"

# Target waktu penyelesaian (SLA) internal per kategori, dalam jam (asumsi proyek)
TARGET_SLA = {
    "Token Gagal Dimasukkan": 24, "Token Belum Diterima": 24, "Listrik Padam": 6,
    "Meter Error": 72, "Tegangan Tidak Stabil": 48, "kWh Cepat Habis": 72, "Lainnya": 72,
}
# Ejaan yang ditemukan di data mentah -> nama baku
EJAAN_KATEGORI = {
    "lstrik padam": "Listrik Padam",
    "token gagal di masukkan": "Token Gagal Dimasukkan",
    "token blm diterima": "Token Belum Diterima",
    "meter eror": "Meter Error",
    "tegangan tdk stabil": "Tegangan Tidak Stabil",
    "lain-lain": "Lainnya",
}
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

log = []  # (masalah, tindakan, jumlah baris)
df = pd.read_csv(RAW, dtype=str, keep_default_na=False)
n_awal = len(df)

# 1. Baris ganda
dup = df.duplicated().sum()
df = df.drop_duplicates().reset_index(drop=True)
log.append(("Baris ganda (tiket terkirim dua kali)", "Dihapus", dup))
assert df["id_tiket"].is_unique, "id_tiket masih ganda setelah hapus duplikat"

# 2a. Nama unit
asli = df["unit_layanan"].copy()
u = df["unit_layanan"].str.strip().str.lower().str.replace(r"\s+", " ", regex=True)
u = u.where(u.str.startswith("unit "), "unit " + u)
df["unit_layanan"] = u.str.title()
log.append(("Nama unit tidak seragam (huruf besar/kecil, spasi, tanpa kata \"Unit\")",
            "Diseragamkan", (asli != df["unit_layanan"]).sum()))

# 2b. Kategori
asli = df["kategori"].copy()
k = df["kategori"].str.strip().str.replace(r"\s+", " ", regex=True)
baku = {nama.lower(): nama for nama in TARGET_SLA}
df["kategori"] = k.str.lower().map(lambda x: baku.get(x) or EJAAN_KATEGORI.get(x))
assert df["kategori"].notna().all(), "Ada kategori yang belum dikenali"
log.append(("Penulisan kategori tidak seragam atau salah ketik", "Dipetakan ke 7 nama baku",
            (asli != df["kategori"]).sum()))

# 3. Tanggal dengan dua format
t1 = pd.to_datetime(df["waktu_lapor"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
t2 = pd.to_datetime(df["waktu_lapor"], format="%d/%m/%Y %H:%M", errors="coerce")
log.append(("waktu_lapor memakai format DD/MM/YYYY", "Dikonversi ke format standar", t1.isna().sum()))
df["waktu_lapor"] = t1.fillna(t2)
assert df["waktu_lapor"].notna().all(), "Ada waktu_lapor yang gagal dibaca"
df["waktu_selesai"] = pd.to_datetime(df["waktu_selesai"].where(df["waktu_selesai"] != ""), format="%Y-%m-%d %H:%M:%S")

# 4. Daya
kosong = df["daya_va"].eq("").sum()
pakai_satuan = df["daya_va"].str.contains("VA", regex=False).sum()
df["daya_va"] = pd.to_numeric(df["daya_va"].str.replace("VA", "", regex=False).str.strip(),
                              errors="coerce").astype("Int64")
log.append(("Daya tertulis dengan satuan \"VA\" (\"900 VA\" bukan 900)", "Satuan dihapus, jadi angka",
            pakai_satuan))
log.append(("Daya kosong", "Dibiarkan kosong (tidak ditebak)", kosong))

# 5. Kanal kosong
kosong = df["kanal"].eq("").sum()
df["kanal"] = df["kanal"].replace("", "Tidak Diketahui")
log.append(("Kanal pengaduan kosong", "Diisi \"Tidak Diketahui\"", kosong))

# 6. Durasi & salah input waktu
df["rating_kepuasan"] = pd.to_numeric(df["rating_kepuasan"].where(df["rating_kepuasan"] != "-")).astype("Int64")
durasi = (df["waktu_selesai"] - df["waktu_lapor"]).dt.total_seconds() / 3600
salah = durasi < 0
log.append(("waktu_selesai lebih awal dari waktu_lapor", "Durasi dikosongkan dan ditandai", salah.sum()))
df["durasi_valid"] = np.where(df["status"].eq("Selesai"), (~salah).astype(int), np.nan)
df["durasi_jam"] = durasi.where(~salah).round(2)

# Kolom turunan untuk analisis
df["target_sla_jam"] = df["kategori"].map(TARGET_SLA)
df["tepat_waktu"] = np.where(df["durasi_jam"].isna(), np.nan,
                             (df["durasi_jam"] <= df["target_sla_jam"]).astype(float))
df["tahun"] = df["waktu_lapor"].dt.year
df["bulan"] = df["waktu_lapor"].dt.strftime("%Y-%m")
df["hari_lapor"] = df["waktu_lapor"].dt.dayofweek.map(dict(enumerate(HARI)))
df["jam_lapor"] = df["waktu_lapor"].dt.hour

# Pengaduan ulang: pelanggan yang sama, kategori yang sama, <= 30 hari
df = df.sort_values(["id_pelanggan", "kategori", "waktu_lapor"]).reset_index(drop=True)
g = df.groupby(["id_pelanggan", "kategori"])
jeda_sebelum = df["waktu_lapor"] - g["waktu_lapor"].shift(1)
df["pengaduan_ulang"] = (jeda_sebelum <= pd.Timedelta(days=30)).astype(int)
lapor_berikut = g["waktu_lapor"].shift(-1)
diikuti = (lapor_berikut - df["waktu_selesai"]) <= pd.Timedelta(days=30)
df["diikuti_pengaduan_ulang"] = np.where(df["status"].eq("Selesai"), diikuti.astype(float), np.nan)

df = df.sort_values("waktu_lapor").reset_index(drop=True)
kolom = ["id_tiket", "id_pelanggan", "waktu_lapor", "waktu_selesai", "tahun", "bulan", "hari_lapor",
         "jam_lapor", "unit_layanan", "kategori", "kanal", "daya_va", "status", "durasi_jam",
         "durasi_valid", "target_sla_jam", "tepat_waktu", "rating_kepuasan", "pengaduan_ulang",
         "diikuti_pengaduan_ulang"]
for c in ["durasi_valid", "tepat_waktu", "diikuti_pengaduan_ulang"]:
    df[c] = df[c].astype("Int64")
OUT.parent.mkdir(parents=True, exist_ok=True)
df[kolom].to_csv(OUT, index=False, date_format="%Y-%m-%d %H:%M:%S")

# Laporan pembersihan
baris = "\n".join(f"| {m} | {t} | {'-' if j is None else f'{j:,}'.replace(',', '.')} |" for m, t, j in log)
LAPORAN.parent.mkdir(parents=True, exist_ok=True)
LAPORAN.write_text(
    "# Laporan pembersihan data\n\n"
    f"Data mentah: {n_awal:,} baris. Data bersih: {len(df):,} baris.\n\n".replace(",", ".")
    + "| Masalah | Tindakan | Jumlah baris |\n| --- | --- | --- |\n" + baris + "\n",
    encoding="utf-8")
print(LAPORAN.read_text(encoding="utf-8"))
print(f"Tersimpan -> {OUT.relative_to(ROOT)}")
