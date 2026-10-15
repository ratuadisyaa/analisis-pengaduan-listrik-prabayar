"""
Langkah 1 - Membuat data SIMULASI pengaduan pelanggan listrik prabayar.

PENTING: seluruh data di proyek ini adalah data simulasi (fiktif).
Data ini TIDAK berasal dari PLN atau perusahaan mana pun. Nama unit layanan,
ID pelanggan, dan ID tiket semuanya dibuat oleh skrip ini.

Mengapa simulasi? Data pengaduan asli bersifat rahasia. Simulasi ini meniru
pola yang wajar terjadi pada layanan listrik prabayar agar alur kerja analisis
(pembersihan data, SQL, dashboard, rekomendasi) bisa ditunjukkan secara terbuka.
Semua asumsi pola ditulis di data/README.md.

Keluaran: data/raw/pengaduan_raw.csv (sengaja dibuat "berantakan" seperti data
operasional sungguhan, supaya langkah pembersihan data punya pekerjaan nyata).
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "pengaduan_raw.csv"
rng = np.random.default_rng(2026)

MULAI, SELESAI = pd.Timestamp("2024-01-01"), pd.Timestamp("2025-12-31")
BATAS_DATA = pd.Timestamp("2025-12-31 23:59:59")  # data "ditarik" pada saat ini

# ---------------------------------------------------------------- asumsi --
# Kategori: bobot volume, target SLA internal (jam), median durasi (jam), sebaran
KATEGORI = {
    "Token Gagal Dimasukkan": dict(bobot=0.24, sla=24, median=6.0, sigma=0.95),
    "Token Belum Diterima":   dict(bobot=0.14, sla=24, median=4.0, sigma=1.00),
    "Listrik Padam":          dict(bobot=0.22, sla=6,  median=2.6, sigma=0.75),
    "Meter Error":            dict(bobot=0.12, sla=72, median=30., sigma=0.80),
    "Tegangan Tidak Stabil":  dict(bobot=0.10, sla=48, median=16., sigma=0.80),
    "kWh Cepat Habis":        dict(bobot=0.11, sla=72, median=34., sigma=0.75),
    "Lainnya":                dict(bobot=0.07, sla=72, median=18., sigma=1.00),
}
KAT_TOKEN = {"Token Gagal Dimasukkan", "Token Belum Diterima"}

# Unit layanan fiktif: porsi pelanggan, faktor kecepatan (1 = normal, >1 = lebih lambat)
UNIT = {
    "Unit Pusat":   dict(porsi=0.22, lambat=0.90),
    "Unit Utara":   dict(porsi=0.18, lambat=1.00),
    "Unit Selatan": dict(porsi=0.17, lambat=1.00),
    "Unit Barat":   dict(porsi=0.16, lambat=0.95),
    "Unit Timur":   dict(porsi=0.15, lambat=1.55),  # asumsi: kekurangan petugas lapangan
    "Unit Pesisir": dict(porsi=0.12, lambat=1.20),  # asumsi: wilayah luas, banyak meter tua
}
# Pengali volume kategori tertentu di unit tertentu
UNIT_X_KAT = {
    ("Unit Pesisir", "Meter Error"): 1.9,
    ("Unit Pesisir", "Listrik Padam"): 1.35,
    ("Unit Pusat", "Token Gagal Dimasukkan"): 1.15,
    ("Unit Pusat", "Token Belum Diterima"): 1.15,
}
KANAL = {"Aplikasi Mobile": 0.38, "Call Center": 0.30, "WhatsApp": 0.17,
         "Kantor Layanan": 0.08, "Media Sosial": 0.07}
DAYA = {450: 0.18, 900: 0.34, 1300: 0.26, 2200: 0.14, 3500: 0.05, 5500: 0.03}
LEBARAN = [pd.Timestamp("2024-04-10"), pd.Timestamp("2025-03-31")]
BULAN_HUJAN = {11, 12, 1, 2, 3}
FAKTOR_HARI = [1.10, 1.04, 1.00, 1.00, 0.97, 0.95, 0.94]  # Senin..Minggu


def bobot_jam(kat):
    w = np.ones(24)
    if kat in KAT_TOKEN:          # beli token sepulang kerja
        w[0:6], w[6:10], w[10:18], w[18:23], w[23] = 0.25, 1.0, 1.6, 2.6, 0.6
    elif kat == "Listrik Padam":  # hujan sore hari
        w[0:6], w[6:13], w[13:20], w[20:24] = 0.6, 1.0, 1.7, 1.2
    else:                         # keluhan teknis lain: jam aktif
        w[0:6], w[6:8], w[8:17], w[17:22], w[22:24] = 0.2, 1.0, 1.8, 1.3, 0.5
    return w / w.sum()


JAM_W = {k: bobot_jam(k) for k in KATEGORI}
units, porsi = list(UNIT), np.array([u["porsi"] for u in UNIT.values()])
pool_pelanggan = {u: rng.choice(np.arange(1_000_000, 9_999_999), 25_000, replace=False) for u in units}


def faktor_musim(kat, tgl):
    f = 1.0
    if kat == "Listrik Padam":
        f *= 1.6 if tgl.month in BULAN_HUJAN else (1.15 if tgl.month in (4, 10) else 1.0)
    if kat == "Tegangan Tidak Stabil":
        f *= 1.35 if tgl.month in BULAN_HUJAN else 1.0
    if kat in KAT_TOKEN:
        if tgl.day <= 5:
            f *= 1.35            # awal bulan: setelah gajian
        elif tgl.day >= 25:
            f *= 1.15
        if any(0 <= (l - tgl).days <= 10 for l in LEBARAN):
            f *= 1.8             # pembelian token menjelang Lebaran
    if kat != "Listrik Padam":
        f *= FAKTOR_HARI[tgl.dayofweek]
    return f


def durasi_jam(kat, unit, waktu):
    k = KATEGORI[kat]
    m = k["median"] * UNIT[unit]["lambat"]
    if kat != "Listrik Padam":
        if waktu.dayofweek >= 5:
            m *= 1.30            # akhir pekan: petugas lebih sedikit
        if waktu.hour >= 22 or waktu.hour < 6:
            m *= 1.20
    elif waktu.month in BULAN_HUJAN:
        m *= 1.30                # gangguan menumpuk saat musim hujan
    if unit == "Unit Pesisir" and kat == "Meter Error":
        m *= 1.30                # suku cadang meter harus didatangkan
    return float(rng.lognormal(np.log(m), k["sigma"]))


def buat_tiket(waktu, unit, kat, pelanggan, ulang=False):
    jam = durasi_jam(kat, unit, waktu) * (1.1 if ulang else 1.0)
    selesai = waktu + pd.Timedelta(hours=jam)
    status = "Selesai"
    if rng.random() < 0.012:
        status, selesai = "Dibatalkan", pd.NaT
    elif selesai > BATAS_DATA:
        status, selesai = "Dalam Proses", pd.NaT
    rating = np.nan
    if status == "Selesai" and rng.random() < 0.35:   # 35% pelanggan mengisi survei
        r = min(jam / KATEGORI[kat]["sla"], 3.0)
        rating = int(np.clip(round(4.5 - 0.9 * r - (0.4 if ulang else 0) + rng.normal(0, 0.6)), 1, 5))
    return dict(waktu_lapor=waktu, waktu_selesai=selesai, unit_layanan=unit, kategori=kat,
                id_pelanggan=pelanggan, status=status, rating_kepuasan=rating, _jam=jam)


# ------------------------------------------------------------ simulasi --
rows = []
hari_total = (SELESAI - MULAI).days
for i, tgl in enumerate(pd.date_range(MULAI, SELESAI, freq="D")):
    dasar = 26 + 6 * i / hari_total                      # volume naik pelan
    for kat, k in KATEGORI.items():
        n = rng.poisson(dasar * k["bobot"] * faktor_musim(kat, tgl))
        if n == 0:
            continue
        w = porsi * np.array([UNIT_X_KAT.get((u, kat), 1.0) for u in units])
        pilih_unit = rng.choice(units, n, p=w / w.sum())
        jam = rng.choice(24, n, p=JAM_W[kat])
        menit = rng.integers(0, 60, n)
        for u, h, mnt in zip(pilih_unit, jam, menit):
            waktu = tgl + pd.Timedelta(hours=int(h), minutes=int(mnt))
            t = buat_tiket(waktu, u, kat, int(rng.choice(pool_pelanggan[u])))
            rows.append(t)
            # Pengaduan ulang: lebih mungkin jika penanganan pertama melewati SLA
            if t["status"] == "Selesai":
                p = 0.045 if t["_jam"] <= k["sla"] else 0.15
                p *= {"Meter Error": 1.4, "kWh Cepat Habis": 1.5}.get(kat, 1.0)
                if rng.random() < p:
                    jeda = 1 + rng.exponential(5)
                    w2 = t["waktu_selesai"] + pd.Timedelta(days=float(jeda))
                    if jeda <= 30 and w2 <= BATAS_DATA:
                        rows.append(buat_tiket(w2.floor("min"), u, kat, t["id_pelanggan"], ulang=True))

df = pd.DataFrame(rows).sort_values("waktu_lapor").reset_index(drop=True)
df["id_tiket"] = [f"TKT-{w:%Y%m}-{i:05d}" for i, w in enumerate(df["waktu_lapor"], start=1)]
df["id_pelanggan"] = "PLG" + df["id_pelanggan"].astype(str)
df["kanal"] = rng.choice(list(KANAL), len(df), p=list(KANAL.values()))
df["daya_va"] = rng.choice(list(DAYA), len(df), p=list(DAYA.values())).astype(object)

# ------------------------------------------- bikin "berantakan" (realistis) --
n = len(df)
fmt = df["waktu_lapor"].dt.strftime("%Y-%m-%d %H:%M:%S")
alt = rng.random(n) < 0.10                                  # 10% format tanggal lain
fmt[alt] = df.loc[alt, "waktu_lapor"].dt.strftime("%d/%m/%Y %H:%M")
df["waktu_lapor"] = fmt
df["waktu_selesai"] = df["waktu_selesai"].dt.strftime("%Y-%m-%d %H:%M:%S")

VARIAN_KAT = {
    "Listrik Padam": ["listrik padam", "LISTRIK PADAM", "Listrik  Padam", "Lstrik Padam"],
    "Token Gagal Dimasukkan": ["token gagal dimasukkan", "Token gagal di masukkan", "TOKEN GAGAL DIMASUKKAN"],
    "Token Belum Diterima": ["token belum diterima", "Token Blm Diterima"],
    "Meter Error": ["meter error", "METER ERROR", "Meter Eror"],
    "Tegangan Tidak Stabil": ["tegangan tidak stabil", "Tegangan Tdk Stabil"],
    "kWh Cepat Habis": ["KWH Cepat Habis", "kwh cepat habis"],
    "Lainnya": ["lainnya", "Lain-lain"],
}
idx = np.where(rng.random(n) < 0.08)[0]
df.loc[idx, "kategori"] = [rng.choice(VARIAN_KAT[k]) for k in df.loc[idx, "kategori"]]
idx = np.where(rng.random(n) < 0.05)[0]
df.loc[idx, "unit_layanan"] = [rng.choice([u.upper(), u.lower() + " ", u.replace("Unit ", "")])
                               for u in df.loc[idx, "unit_layanan"]]
idx = rng.random(n) < 0.30
df.loc[idx, "daya_va"] = df.loc[idx, "daya_va"].astype(str) + " VA"
df.loc[rng.random(n) < 0.005, "daya_va"] = ""
df.loc[rng.random(n) < 0.01, "kanal"] = ""
# Kesalahan input: waktu selesai tercatat lebih awal dari waktu lapor
sel = df.index[df["status"].eq("Selesai")]
salah = rng.choice(sel, int(len(sel) * 0.003), replace=False)
df.loc[salah, "waktu_selesai"] = (pd.to_datetime(df.loc[salah, "waktu_selesai"])
                                  - pd.Timedelta(days=2)).dt.strftime("%Y-%m-%d %H:%M:%S")
df["rating_kepuasan"] = df["rating_kepuasan"].map(lambda r: "-" if pd.isna(r) else str(int(r)))
df = df.drop(columns="_jam")
# Baris ganda karena tombol "kirim" ditekan dua kali
df = pd.concat([df, df.sample(frac=0.015, random_state=7)]).sort_values("id_tiket")

kolom = ["id_tiket", "id_pelanggan", "waktu_lapor", "waktu_selesai", "unit_layanan", "kategori",
         "kanal", "daya_va", "status", "rating_kepuasan"]
OUT.parent.mkdir(parents=True, exist_ok=True)
df[kolom].to_csv(OUT, index=False)
print(f"Tersimpan {len(df):,} baris -> {OUT.relative_to(ROOT)}")
