-- =====================================================================
-- 03. Kinerja per kategori pengaduan
-- Pertanyaan : Kategori apa yang paling banyak dan paling sering
--              melewati target waktu penyelesaian?
-- Konsep SQL : window function SUM() OVER () untuk menghitung porsi (%)
-- =====================================================================
SELECT
    kategori,
    COUNT(*)                                                  AS total_tiket,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)        AS porsi_persen,
    MAX(target_sla_jam)                                       AS target_sla_jam,
    ROUND(100.0 * AVG(tepat_waktu), 1)                        AS persen_tepat_waktu,
    ROUND(AVG(durasi_jam), 1)                                 AS rata_durasi_jam,
    ROUND(AVG(rating_kepuasan), 2)                            AS rata_kepuasan
FROM pengaduan
GROUP BY kategori
ORDER BY total_tiket DESC;
