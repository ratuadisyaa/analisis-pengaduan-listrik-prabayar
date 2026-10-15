-- =====================================================================
-- 02. Tren bulanan
-- Pertanyaan : Kapan pengaduan meningkat dan ketepatan waktu menurun?
-- Konsep SQL : GROUP BY bulan, CASE WHEN untuk menandai musim hujan
-- =====================================================================
SELECT
    bulan,
    CASE WHEN CAST(substr(bulan, 6, 2) AS INTEGER) IN (11, 12, 1, 2, 3)
         THEN 'Musim hujan' ELSE 'Musim kemarau' END                    AS musim,
    COUNT(*)                                                            AS total_tiket,
    SUM(CASE WHEN kategori = 'Listrik Padam' THEN 1 ELSE 0 END)         AS tiket_listrik_padam,
    ROUND(100.0 * AVG(tepat_waktu), 1)                                  AS persen_tepat_waktu
FROM pengaduan
GROUP BY bulan
ORDER BY bulan;
