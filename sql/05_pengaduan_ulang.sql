-- =====================================================================
-- 05. Dampak keterlambatan terhadap pengaduan ulang dan kepuasan
-- Pertanyaan : Apakah tiket yang terlambat ditangani lebih sering
--              diikuti pengaduan ulang dan rating yang lebih rendah?
-- Konsep SQL : LEAD() OVER (PARTITION BY ... ORDER BY ...), julianday()
-- Definisi   : sebuah tiket "diikuti pengaduan ulang" jika pelanggan yang
--              sama melapor lagi untuk kategori yang sama paling lama
--              30 hari setelah tiket itu selesai.
-- =====================================================================
WITH urutan AS (
    SELECT
        id_tiket,
        tepat_waktu,
        rating_kepuasan,
        waktu_selesai,
        LEAD(waktu_lapor) OVER (
            PARTITION BY id_pelanggan, kategori
            ORDER BY waktu_lapor
        ) AS lapor_berikutnya
    FROM pengaduan
),
ditandai AS (
    SELECT
        *,
        CASE WHEN lapor_berikutnya IS NOT NULL
              AND julianday(lapor_berikutnya) - julianday(waktu_selesai) <= 30
             THEN 1 ELSE 0 END AS diikuti_ulang
    FROM urutan
    WHERE tepat_waktu IS NOT NULL          -- hanya tiket selesai dengan durasi valid
)
SELECT
    CASE tepat_waktu WHEN 1 THEN 'Tepat waktu' ELSE 'Melewati SLA' END   AS kelompok,
    COUNT(*)                                                          AS jumlah_tiket,
    ROUND(100.0 * AVG(diikuti_ulang), 1)                              AS persen_diikuti_pengaduan_ulang,
    ROUND(AVG(rating_kepuasan), 2)                                    AS rata_kepuasan
FROM ditandai
GROUP BY tepat_waktu
ORDER BY tepat_waktu DESC;
