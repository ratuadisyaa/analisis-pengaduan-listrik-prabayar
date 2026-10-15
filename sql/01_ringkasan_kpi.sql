-- =====================================================================
-- 01. Ringkasan KPI per tahun
-- Pertanyaan : Bagaimana kinerja layanan pengaduan secara keseluruhan?
-- Konsep SQL : COUNT, SUM, AVG, CASE WHEN, GROUP BY, UNION ALL
-- Catatan    : AVG() mengabaikan nilai NULL. Kolom tepat_waktu bernilai
--              NULL untuk tiket yang belum selesai, dibatalkan, atau
--              durasinya tidak valid, sehingga tidak ikut dihitung.
-- =====================================================================
SELECT
    CAST(tahun AS TEXT)                                   AS periode,
    COUNT(*)                                              AS total_tiket,
    SUM(CASE WHEN status = 'Selesai' THEN 1 ELSE 0 END)   AS tiket_selesai,
    ROUND(100.0 * AVG(tepat_waktu), 1)                    AS persen_tepat_waktu,
    ROUND(AVG(durasi_jam), 1)                             AS rata_durasi_jam,
    ROUND(AVG(rating_kepuasan), 2)                        AS rata_kepuasan,
    ROUND(100.0 * AVG(pengaduan_ulang), 1)                AS persen_pengaduan_ulang
FROM pengaduan
GROUP BY tahun

UNION ALL

SELECT
    'Total',
    COUNT(*),
    SUM(CASE WHEN status = 'Selesai' THEN 1 ELSE 0 END),
    ROUND(100.0 * AVG(tepat_waktu), 1),
    ROUND(AVG(durasi_jam), 1),
    ROUND(AVG(rating_kepuasan), 2),
    ROUND(100.0 * AVG(pengaduan_ulang), 1)
FROM pengaduan;
