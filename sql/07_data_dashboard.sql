-- =====================================================================
-- 07. Data ringkas untuk dashboard (bulan x unit x kategori)
-- Dashboard menghitung ulang semua angka dari tabel ringkas ini saat
-- filter diubah, sehingga data per tiket tidak perlu dikirim ke browser.
-- =====================================================================
SELECT
    bulan,
    unit_layanan,
    kategori,
    COUNT(*)                                                         AS n,
    SUM(CASE WHEN tepat_waktu IS NOT NULL THEN 1 ELSE 0 END)         AS n_dinilai,
    SUM(CASE WHEN tepat_waktu = 1 THEN 1 ELSE 0 END)                 AS n_tepat,
    ROUND(SUM(durasi_jam), 2)                                        AS total_durasi,
    SUM(CASE WHEN durasi_jam IS NOT NULL THEN 1 ELSE 0 END)          AS n_durasi,
    SUM(CASE WHEN rating_kepuasan IS NOT NULL THEN 1 ELSE 0 END)     AS n_rating,
    SUM(COALESCE(rating_kepuasan, 0))                                AS total_rating,
    SUM(pengaduan_ulang)                                             AS n_ulang,
    SUM(CASE WHEN tepat_waktu = 1 AND diikuti_pengaduan_ulang = 1 THEN 1 ELSE 0 END) AS n_tepat_diikuti,
    SUM(CASE WHEN tepat_waktu = 0 AND diikuti_pengaduan_ulang = 1 THEN 1 ELSE 0 END) AS n_telat_diikuti,
    SUM(CASE WHEN tepat_waktu = 1 AND rating_kepuasan IS NOT NULL THEN 1 ELSE 0 END)  AS n_rating_tepat,
    SUM(CASE WHEN tepat_waktu = 1 THEN COALESCE(rating_kepuasan, 0) ELSE 0 END)       AS total_rating_tepat,
    SUM(CASE WHEN tepat_waktu = 0 AND rating_kepuasan IS NOT NULL THEN 1 ELSE 0 END)  AS n_rating_telat,
    SUM(CASE WHEN tepat_waktu = 0 THEN COALESCE(rating_kepuasan, 0) ELSE 0 END)       AS total_rating_telat
FROM pengaduan
GROUP BY bulan, unit_layanan, kategori
ORDER BY bulan, unit_layanan, kategori;
