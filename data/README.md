# Data: kamus kolom dan asumsi simulasi

> Seluruh data di folder ini adalah **data simulasi** yang dibuat oleh
> `scripts/01_buat_data_simulasi.py`. Data ini tidak berasal dari PLN atau
> perusahaan mana pun. Nama unit, ID pelanggan, dan ID tiket bersifat fiktif.

## Berkas

| Berkas | Isi |
| --- | --- |
| `raw/pengaduan_raw.csv` | Data mentah, sengaja dibuat "berantakan" seperti data operasional (25.602 baris) |
| `processed/pengaduan_bersih.csv` | Data setelah dibersihkan dan diberi kolom turunan (25.224 baris) |

Rincian pembersihan ada di [`../outputs/laporan_pembersihan.md`](../outputs/laporan_pembersihan.md).

## Kamus kolom (data bersih)

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `id_tiket` | teks | Nomor tiket, format `TKT-YYYYMM-nnnnn` |
| `id_pelanggan` | teks | ID pelanggan fiktif |
| `waktu_lapor` | waktu | Saat pengaduan diterima |
| `waktu_selesai` | waktu | Saat tiket ditutup; kosong jika belum selesai atau dibatalkan |
| `tahun`, `bulan`, `hari_lapor`, `jam_lapor` | turunan | Dipecah dari `waktu_lapor` |
| `unit_layanan` | teks | Salah satu dari 6 unit fiktif |
| `kategori` | teks | Salah satu dari 7 kategori pengaduan |
| `kanal` | teks | Aplikasi Mobile, Call Center, WhatsApp, Kantor Layanan, Media Sosial, Tidak Diketahui |
| `daya_va` | angka | Daya tersambung pelanggan (VA) |
| `status` | teks | Selesai, Dalam Proses, Dibatalkan |
| `durasi_jam` | angka | Selisih waktu selesai dan waktu lapor; kosong jika tidak valid |
| `durasi_valid` | 0/1 | 0 jika waktu selesai tercatat lebih awal dari waktu lapor |
| `target_sla_jam` | angka | Target waktu penyelesaian kategori tersebut |
| `tepat_waktu` | 0/1 | 1 jika `durasi_jam` ≤ `target_sla_jam`; kosong jika tidak bisa dinilai |
| `rating_kepuasan` | 1–5 | Hasil survei setelah tiket selesai; kosong jika pelanggan tidak mengisi |
| `pengaduan_ulang` | 0/1 | 1 jika pelanggan yang sama melapor kategori yang sama ≤ 30 hari sebelumnya |
| `diikuti_pengaduan_ulang` | 0/1 | 1 jika pelanggan melapor lagi kategori yang sama ≤ 30 hari setelah tiket ini selesai |

## Target SLA (asumsi proyek)

Target ini adalah asumsi internal untuk perusahaan fiktif, **bukan** angka dari
regulasi atau perusahaan nyata.

| Kategori | Target selesai |
| --- | --- |
| Listrik Padam | 6 jam |
| Token Gagal Dimasukkan | 24 jam |
| Token Belum Diterima | 24 jam |
| Tegangan Tidak Stabil | 48 jam |
| Meter Error | 72 jam |
| kWh Cepat Habis | 72 jam |
| Lainnya | 72 jam |

## Asumsi pola dalam simulasi

Pola di bawah ini sengaja dimasukkan ke simulasi agar data menyerupai kondisi
lapangan. Karena itu, temuan analisis menunjukkan **kemampuan menemukan pola**,
bukan fakta tentang perusahaan mana pun.

- Volume pengaduan naik perlahan dari sekitar 26 menjadi 32 tiket per hari selama 2024–2025.
- Musim hujan (November–Maret): tiket listrik padam ×1,6, tegangan tidak stabil ×1,35, dan penanganan gangguan lebih lambat.
- Pengaduan token meningkat di awal bulan (setelah gajian), pada malam hari (18.00–22.59), dan 10 hari menjelang Lebaran.
- Unit Timur diasumsikan kekurangan petugas lapangan (penanganan ±1,55× lebih lama).
- Unit Pesisir diasumsikan memiliki banyak meter tua (tiket Meter Error ±1,9× lebih banyak) dan wilayah yang luas.
- Tiket non-gangguan yang masuk akhir pekan atau malam hari ditangani lebih lama.
- Tiket yang melewati SLA lebih mungkin diikuti pengaduan ulang (15% dibanding 4,5%) dan mendapat rating lebih rendah.
- 35% pelanggan mengisi survei kepuasan; 1,2% tiket dibatalkan.

## Masalah kualitas data yang sengaja dimasukkan

Baris ganda (1,5%), penulisan kategori dan unit yang tidak seragam, dua format
tanggal, daya dengan dan tanpa satuan "VA", kanal kosong, serta waktu selesai
yang lebih awal dari waktu lapor (0,3% tiket selesai).
