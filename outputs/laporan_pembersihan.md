# Laporan pembersihan data

Data mentah: 25.602 baris. Data bersih: 25.224 baris.

| Masalah | Tindakan | Jumlah baris |
| --- | --- | --- |
| Baris ganda (tiket terkirim dua kali) | Dihapus | 378 |
| Nama unit tidak seragam (huruf besar/kecil, spasi, tanpa kata "Unit") | Diseragamkan | 1.218 |
| Penulisan kategori tidak seragam atau salah ketik | Dipetakan ke 7 nama baku | 2.011 |
| waktu_lapor memakai format DD/MM/YYYY | Dikonversi ke format standar | 2.617 |
| Daya tertulis dengan satuan "VA" ("900 VA" bukan 900) | Satuan dihapus, jadi angka | 7.519 |
| Daya kosong | Dibiarkan kosong (tidak ditebak) | 119 |
| Kanal pengaduan kosong | Diisi "Tidak Diketahui" | 239 |
| waktu_selesai lebih awal dari waktu_lapor | Durasi dikosongkan dan ditandai | 64 |
