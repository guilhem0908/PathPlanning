#### Summary over 26 tracks

| Planner | Median planning time (ms) | Slowest track (s) | Median min clearance (m) | Worst min clearance (m) | Tracks with clearance below 0.7 m | Lowest share between the rows (%) | RRT* segments solved |
|---|---|---|---|---|---|---|---|
| midpoint | 63 | 0.2 | 0.94 | 0.48 | 6 / 26 | 99.5 | - |
| rrt | 27731 | 58.8 | 0.15 | 0.01 | 23 / 26 | 99.5 | 585 / 11998 (5 %) |
| rrt-lsq | 34124 | 73.1 | 0.04 | 0.01 | 25 / 26 | 97.4 | 585 / 11998 (5 %) |

#### The three tracks of the original menu

| Track | Width (m) | Planner | Planning time (ms) | Path length (m) | Min clearance (m) | Between the rows (%) | RRT* segments solved |
|---|---|---|---|---|---|---|---|
| `small_track` | 4.77 | midpoint | 1.2 | 104.1 | 1.92 | 99.5 | - |
| `small_track` | 4.77 | rrt | 82 | 101.5 | 1.14 | 99.5 | 31 / 31 (100 %) |
| `small_track` | 4.77 | rrt-lsq | 109 | 100.1 | 0.58 | 99.5 | 31 / 31 (100 %) |
| `hairpins_increasing_difficulty` | 3.00 | midpoint | 32 | 831.4 | 0.98 | 100.0 | - |
| `hairpins_increasing_difficulty` | 3.00 | rrt | 1434 | 815.4 | 0.16 | 100.0 | 489 / 491 (100 %) |
| `hairpins_increasing_difficulty` | 3.00 | rrt-lsq | 1472 | 812.2 | 0.13 | 100.0 | 489 / 491 (100 %) |
| `peanut` | 4.19 | midpoint | 2.5 | 103.8 | 1.80 | 100.0 | - |
| `peanut` | 4.19 | rrt | 47 | 99.8 | 1.00 | 100.0 | 65 / 65 (100 %) |
| `peanut` | 4.19 | rrt-lsq | 45 | 99.6 | 0.67 | 100.0 | 65 / 65 (100 %) |

<details>
<summary>All 78 runs</summary>

| Track | Width (m) | Planner | Planning time (ms) | Path length (m) | Min clearance (m) | Between the rows (%) | RRT* segments solved |
|---|---|---|---|---|---|---|---|
| `small_track` | 4.77 | midpoint | 1.2 | 104.1 | 1.92 | 99.5 | - |
| `small_track` | 4.77 | rrt | 82 | 101.5 | 1.14 | 99.5 | 31 / 31 (100 %) |
| `small_track` | 4.77 | rrt-lsq | 109 | 100.1 | 0.58 | 99.5 | 31 / 31 (100 %) |
| `hairpins_increasing_difficulty` | 3.00 | midpoint | 32 | 831.4 | 0.98 | 100.0 | - |
| `hairpins_increasing_difficulty` | 3.00 | rrt | 1434 | 815.4 | 0.16 | 100.0 | 489 / 491 (100 %) |
| `hairpins_increasing_difficulty` | 3.00 | rrt-lsq | 1472 | 812.2 | 0.13 | 100.0 | 489 / 491 (100 %) |
| `peanut` | 4.19 | midpoint | 2.5 | 103.8 | 1.80 | 100.0 | - |
| `peanut` | 4.19 | rrt | 47 | 99.8 | 1.00 | 100.0 | 65 / 65 (100 %) |
| `peanut` | 4.19 | rrt-lsq | 45 | 99.6 | 0.67 | 100.0 | 65 / 65 (100 %) |
| `Austin_cones` | 2.21 | midpoint | 42 | 420.1 | 0.98 | 100.0 | - |
| `Austin_cones` | 2.21 | rrt | 33739 | 408.1 | 0.08 | 100.0 | 0 / 534 (0 %) |
| `Austin_cones` | 2.21 | rrt-lsq | 39801 | 402.8 | 0.03 | 99.6 | 0 / 534 (0 %) |
| `BrandsHatch_cones` | 2.21 | midpoint | 26 | 356.0 | 0.99 | 100.0 | - |
| `BrandsHatch_cones` | 2.21 | rrt | 23175 | 351.5 | 0.35 | 100.0 | 0 / 436 (0 %) |
| `BrandsHatch_cones` | 2.21 | rrt-lsq | 28508 | 350.5 | 0.02 | 99.9 | 0 / 436 (0 %) |
| `Budapest_cones` | 2.21 | midpoint | 67 | 402.0 | 0.98 | 100.0 | - |
| `Budapest_cones` | 2.21 | rrt | 29778 | 394.1 | 0.27 | 100.0 | 0 / 494 (0 %) |
| `Budapest_cones` | 2.21 | rrt-lsq | 32253 | 391.1 | 0.06 | 99.8 | 0 / 494 (0 %) |
| `Catalunya_cones` | 2.20 | midpoint | 82 | 416.1 | 0.84 | 100.0 | - |
| `Catalunya_cones` | 2.20 | rrt | 27748 | 407.9 | 0.14 | 100.0 | 0 / 512 (0 %) |
| `Catalunya_cones` | 2.20 | rrt-lsq | 32658 | 404.9 | 0.04 | 99.9 | 0 / 512 (0 %) |
| `Hockenheim_cones` | 2.21 | midpoint | 46 | 358.5 | 0.55 | 100.0 | - |
| `Hockenheim_cones` | 2.21 | rrt | 21848 | 349.5 | 0.07 | 99.9 | 0 / 441 (0 %) |
| `Hockenheim_cones` | 2.21 | rrt-lsq | 25356 | 346.3 | 0.01 | 99.6 | 0 / 441 (0 %) |
| `IMS_cones` | 2.21 | midpoint | 36 | 293.0 | 0.99 | 100.0 | - |
| `IMS_cones` | 2.21 | rrt | 15785 | 292.5 | 0.89 | 100.0 | 0 / 375 (0 %) |
| `IMS_cones` | 2.21 | rrt-lsq | 18114 | 292.9 | 1.01 | 100.0 | 0 / 375 (0 %) |
| `Melbourne_cones` | 2.21 | midpoint | 89 | 473.3 | 0.89 | 100.0 | - |
| `Melbourne_cones` | 2.21 | rrt | 45994 | 466.3 | 0.21 | 100.0 | 0 / 584 (0 %) |
| `Melbourne_cones` | 2.21 | rrt-lsq | 58133 | 463.6 | 0.04 | 99.9 | 0 / 584 (0 %) |
| `MexicoCity_cones` | 2.20 | midpoint | 51 | 355.0 | 0.78 | 100.0 | - |
| `MexicoCity_cones` | 2.20 | rrt | 27047 | 345.6 | 0.09 | 99.9 | 0 / 438 (0 %) |
| `MexicoCity_cones` | 2.20 | rrt-lsq | 35591 | 341.3 | 0.05 | 98.5 | 0 / 438 (0 %) |
| `Montreal_cones` | 2.21 | midpoint | 48 | 283.3 | 0.59 | 100.0 | - |
| `Montreal_cones` | 2.21 | rrt | 19776 | 274.0 | 0.03 | 100.0 | 0 / 348 (0 %) |
| `Montreal_cones` | 2.21 | rrt-lsq | 23147 | 270.4 | 0.08 | 99.5 | 0 / 348 (0 %) |
| `Monza_cones` | 2.20 | midpoint | 100 | 445.2 | 0.63 | 100.0 | - |
| `Monza_cones` | 2.20 | rrt | 58788 | 441.0 | 0.18 | 99.9 | 0 / 549 (0 %) |
| `Monza_cones` | 2.20 | rrt-lsq | 73140 | 439.9 | 0.05 | 99.9 | 0 / 549 (0 %) |
| `MoscowRaceway_cones` | 2.22 | midpoint | 171 | 321.9 | 1.00 | 100.0 | - |
| `MoscowRaceway_cones` | 2.22 | rrt | 35068 | 310.8 | 0.21 | 100.0 | 0 / 412 (0 %) |
| `MoscowRaceway_cones` | 2.22 | rrt-lsq | 40717 | 305.0 | 0.02 | 98.7 | 0 / 412 (0 %) |
| `Nuerburgring_cones` | 2.21 | midpoint | 97 | 445.4 | 0.96 | 100.0 | - |
| `Nuerburgring_cones` | 2.21 | rrt | 53651 | 434.8 | 0.12 | 99.7 | 0 / 549 (0 %) |
| `Nuerburgring_cones` | 2.21 | rrt-lsq | 52784 | 429.8 | 0.03 | 98.7 | 0 / 549 (0 %) |
| `Oschersleben_cones` | 2.21 | midpoint | 50 | 260.0 | 0.92 | 100.0 | - |
| `Oschersleben_cones` | 2.21 | rrt | 14838 | 251.3 | 0.24 | 100.0 | 0 / 317 (0 %) |
| `Oschersleben_cones` | 2.21 | rrt-lsq | 17522 | 246.8 | 0.02 | 97.4 | 0 / 317 (0 %) |
| `Sakhir_cones` | 2.21 | midpoint | 109 | 440.3 | 0.71 | 100.0 | - |
| `Sakhir_cones` | 2.21 | rrt | 37140 | 429.9 | 0.02 | 99.8 | 0 / 544 (0 %) |
| `Sakhir_cones` | 2.21 | rrt-lsq | 42294 | 426.3 | 0.03 | 98.9 | 0 / 544 (0 %) |
| `SaoPaulo_cones` | 2.21 | midpoint | 58 | 344.1 | 0.96 | 100.0 | - |
| `SaoPaulo_cones` | 2.21 | rrt | 22983 | 336.5 | 0.14 | 100.0 | 0 / 439 (0 %) |
| `SaoPaulo_cones` | 2.21 | rrt-lsq | 29644 | 333.5 | 0.04 | 98.9 | 0 / 439 (0 %) |
| `Sepang_cones` | 2.21 | midpoint | 107 | 486.4 | 0.98 | 100.0 | - |
| `Sepang_cones` | 2.21 | rrt | 44204 | 476.5 | 0.19 | 100.0 | 0 / 600 (0 %) |
| `Sepang_cones` | 2.21 | rrt-lsq | 47282 | 472.1 | 0.02 | 99.4 | 0 / 600 (0 %) |
| `Shanghai_cones` | 2.20 | midpoint | 89 | 496.4 | 0.48 | 100.0 | - |
| `Shanghai_cones` | 2.20 | rrt | 42073 | 484.4 | 0.01 | 99.7 | 0 / 615 (0 %) |
| `Shanghai_cones` | 2.20 | rrt-lsq | 46960 | 479.7 | 0.02 | 98.8 | 0 / 615 (0 %) |
| `Silverstone_cones` | 2.21 | midpoint | 86 | 457.4 | 0.98 | 100.0 | - |
| `Silverstone_cones` | 2.21 | rrt | 34622 | 449.5 | 0.21 | 100.0 | 0 / 563 (0 %) |
| `Silverstone_cones` | 2.21 | rrt-lsq | 41006 | 445.4 | 0.01 | 99.8 | 0 / 563 (0 %) |
| `Sochi_cones` | 2.21 | midpoint | 73 | 462.5 | 0.72 | 100.0 | - |
| `Sochi_cones` | 2.21 | rrt | 38195 | 454.2 | 0.04 | 100.0 | 0 / 571 (0 %) |
| `Sochi_cones` | 2.21 | rrt-lsq | 41395 | 451.4 | 0.03 | 99.4 | 0 / 571 (0 %) |
| `Spa_cones` | 2.21 | midpoint | 107 | 553.9 | 0.95 | 100.0 | - |
| `Spa_cones` | 2.21 | rrt | 49706 | 544.0 | 0.02 | 99.8 | 0 / 685 (0 %) |
| `Spa_cones` | 2.21 | rrt-lsq | 55341 | 540.0 | 0.04 | 99.4 | 0 / 685 (0 %) |
| `Spielberg_cones` | 2.21 | midpoint | 48 | 342.2 | 0.57 | 100.0 | - |
| `Spielberg_cones` | 2.21 | rrt | 18256 | 337.0 | 0.05 | 100.0 | 0 / 421 (0 %) |
| `Spielberg_cones` | 2.21 | rrt-lsq | 22208 | 335.8 | 0.03 | 99.6 | 0 / 421 (0 %) |
| `YasMarina_cones` | 2.22 | midpoint | 64 | 396.4 | 0.67 | 100.0 | - |
| `YasMarina_cones` | 2.22 | rrt | 27287 | 382.6 | 0.04 | 99.8 | 0 / 508 (0 %) |
| `YasMarina_cones` | 2.22 | rrt-lsq | 35985 | 377.9 | 0.04 | 98.5 | 0 / 508 (0 %) |
| `Zandvoort_cones` | 2.21 | midpoint | 61 | 387.3 | 0.85 | 100.0 | - |
| `Zandvoort_cones` | 2.21 | rrt | 27714 | 379.4 | 0.22 | 100.0 | 0 / 476 (0 %) |
| `Zandvoort_cones` | 2.21 | rrt-lsq | 32524 | 376.0 | 0.06 | 99.7 | 0 / 476 (0 %) |

</details>

Seed 0 for every run. Width is the median distance from a blue cone to the nearest yellow cone. Computing time: 1627 s summed over the runs, 547 s wall clock with 3 processes (Python 3.14.2, NumPy 2.3.5, SciPy 1.17.1, Windows AMD64, 32 logical CPUs, no GPU). The planning times were taken while the runs shared the machine, so they are indicative.
