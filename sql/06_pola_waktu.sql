-- =====================================================================
-- 06. Pola waktu pelaporan (hari x rentang jam)
-- Pertanyaan : Kapan beban pengaduan paling tinggi, untuk mengatur
--              jadwal petugas call center dan lapangan?
-- Konsep SQL : pivot dengan SUM(CASE WHEN ...), ORDER BY dengan CASE
-- =====================================================================
SELECT
    hari_lapor,
    SUM(CASE WHEN jam_lapor BETWEEN 0  AND 5  THEN 1 ELSE 0 END) AS jam_00_05,
    SUM(CASE WHEN jam_lapor BETWEEN 6  AND 11 THEN 1 ELSE 0 END) AS jam_06_11,
    SUM(CASE WHEN jam_lapor BETWEEN 12 AND 17 THEN 1 ELSE 0 END) AS jam_12_17,
    SUM(CASE WHEN jam_lapor BETWEEN 18 AND 23 THEN 1 ELSE 0 END) AS jam_18_23,
    COUNT(*)                                                     AS total
FROM pengaduan
GROUP BY hari_lapor
ORDER BY CASE hari_lapor
    WHEN 'Senin' THEN 1 WHEN 'Selasa' THEN 2 WHEN 'Rabu' THEN 3 WHEN 'Kamis' THEN 4
    WHEN 'Jumat' THEN 5 WHEN 'Sabtu' THEN 6 ELSE 7 END;
