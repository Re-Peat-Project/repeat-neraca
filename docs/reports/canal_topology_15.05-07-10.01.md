# Canal layer audit, 15.05-07-10.01

Written by `scripts/check_canal_topology.py` from `00_inputs/canals.gpkg` (class `KET_KANAL`), snap 15 m, gap 150 m. Counts show where the layer is open or inconsistent; they do not say which class is right.

| class     |   segments |   length km |   dangle ends |   segments with a likely gap |   isolated stubs |   length in components that reach a river, edge or primary (%) |   class flips |
|:----------|-----------:|------------:|--------------:|-----------------------------:|-----------------:|---------------------------------------------------------------:|--------------:|
| primary   |        939 |      1687.6 |           601 |                           92 |              154 |                                                          100   |           126 |
| secondary |       1255 |      1954.1 |           581 |                          114 |               93 |                                                           91.4 |           319 |
| tertiary  |       2858 |      2921.9 |          1397 |                          479 |              297 |                                                           84.4 |           581 |

Components: 734; the largest holds 42% of the length; 91% of the length is in components that reach a river, the KHG edge or a primary canal; 453 components are a single segment.

