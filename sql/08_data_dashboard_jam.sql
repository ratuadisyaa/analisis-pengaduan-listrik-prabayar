-- =====================================================================
-- 08. Data ringkas untuk peta panas hari x jam di dashboard
-- =====================================================================
SELECT tahun, unit_layanan, kategori, hari_lapor, jam_lapor, COUNT(*) AS n
FROM pengaduan
GROUP BY tahun, unit_layanan, kategori, hari_lapor, jam_lapor;
