# Field survey and gridded inputs, 14.10.03_pulau_tebing_tinggi

`python scripts/check_field_inputs.py --khg 14.10.03 --source <survey>`. Survey: Tebingtinggi.csv, 1385 points, 1132 on peat, 253 on mineral soil.

## Zero water tables

329 of 1132 peat points have a water table of 0. The ponding column is 0 everywhere.

Share of zeros by field team (groups with at least 30 peat points): joperi 91% of 35; munar 88% of 49; rizki 80% of 44; iswatul 62% of 42; putra 57% of 63; afrizal 56% of 41; iskandar 50% of 56; hendra 27% of 51; rahmat 15% of 46; (none) 12% of 181; wan 11% of 38; wendi 8% of 51; erwin 8% of 40; adhimas 5% of 38; ahmad sulaiman 3% of 36; prima 0% of 34; susanto 0% of 36.

Share of zeros by land use (groups with at least 30 peat points): mangrove 91% of 105; kebun campuran 30% of 37; perkebunan 29% of 314; perkebunan, semak belukar 20% of 55; hutan, semak belukar 18% of 82; semak belukar 17% of 138; hutan 15% of 255.

## KHG and canals

KHG area 1,381 km2 (EPSG:32648). Canal length inside the KHG: Kanal Primer 96 km; Kanal Sekunder 408 km; Kanal Tersier 837 km (1421 lines).

Canal blocks in 00_inputs/blocks.gpkg: 168; columns OBJECTID_1, OBJECTID, PULAU_1, PROV_2023, KABKO_2023, KEC_2023, DESA_2023, Kodefikasi, KHG, Anggaran, Kegiatan, Pekerjaan, Pelaksana, X, Y, Tipe, Jenis, Bahan, Kode_Renca, Tahun, Source, SISFO, Detail, PERUSAHAAN, PERIJINAN, KODE_PT, DATA, LONGITUDE, LATITUDE, KETERANGAN, Fungsi_KWS, FKw.

## Peat masks against the field record

| layer | marks peat at field peat points | at field mineral points |
|---|---|---|
| GFW peat extent (00_inputs/national) | 99% | 99% |
| peat-depth raster > 0 (00_inputs/peat_depth.tif) | 78% | 82% |

Peat-depth raster (cm) against the measured thickness at 880 peat points: Pearson r 0.10, median ratio 0.92.

## DTMs against the survey elevation

| DTM | n | median DTM (m) | median survey (m) | Pearson r | median difference (m) |
|---|---|---|---|---|---|
| deltadtm | 1376 | 6.62 | 6.84 | 0.91 | -0.37 |
| demnas | 1384 | 8.38 | 6.82 | 0.81 | 1.86 |

## SiTMAT stations (00_inputs/sitmat/daily_long.csv, unflagged days)

| kind | station | days | median (cm) | min (cm) | max (cm) |
|---|---|---|---|---|---|
| community | MTI-0QPGP748RCSW | 76 | -150.0 | -198 | 2 |
| community | MTI-778N952JF9Q9 | 76 | -148.5 | -188 | 2 |
| community | MTI-HPDWC0NK0G2E | 76 | -152.5 | -177 | 2 |
| community | MTI-X1R4W07JKW0U | 0 | nan | nan | nan |
| concession | 14_NSP:D034539 | 200 | -21.0 | -50 | 8 |
| concession | 14_NSP:I029429 | 201 | -23.8 | -63 | 7 |
| concession | 14_NSP:N021208 | 31 | -38.9 | -78 | 0 |
| concession | 14_NSP:Q015357 | 201 | -22.0 | -51 | 22 |
| concession | 14_NSP:S010343 | 201 | -24.0 | -52 | 6 |
| concession | 14_NSP:U004104 | 201 | -17.0 | -54 | 1 |

The survey does not say how its elevations were measured, so agreement with a DTM is not evidence of DTM quality on its own.

