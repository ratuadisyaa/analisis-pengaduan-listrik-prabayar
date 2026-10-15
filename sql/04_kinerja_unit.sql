-- =====================================================================
-- 04. Kinerja per unit layanan
-- Pertanyaan : Unit mana yang paling jauh dari target 90% tepat waktu?
-- Konsep SQL : CTE (WITH), RANK() OVER, selisih terhadap target
-- =====================================================================
WITH per_unit AS (
    SELECT
        unit_layanan,
        COUNT(*)                              AS total_tiket,
        ROUND(100.0 * AVG(tepat_waktu), 1)    AS persen_tepat_waktu,
        ROUND(AVG(durasi_jam), 1)             AS rata_durasi_jam,
        ROUND(AVG(rating_kepuasan), 2)        AS rata_kepuasan
    FROM pengaduan
    GROUP BY unit_layanan
)
SELECT
    RANK() OVER (ORDER BY persen_tepat_waktu ASC)   AS peringkat_terendah,
    unit_layanan,
    total_tiket,
    persen_tepat_waktu,
    ROUND(persen_tepat_waktu - 90, 1)               AS selisih_dari_target_90,
    rata_durasi_jam,
    rata_kepuasan
FROM per_unit
ORDER BY peringkat_terendah;
