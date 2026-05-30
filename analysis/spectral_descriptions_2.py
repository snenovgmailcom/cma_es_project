import pandas as pd
import numpy as np
from scipy.stats import spearmanr

# Load spectral CSV
spec = pd.read_csv("spectral_desc_cec2017_d10.csv")
agg = spec.groupby(["suite","fnum"]).median(numeric_only=True).reset_index()
# Keep only what we have
agg = agg[agg["suite"] == "cec2017"]
# Add gap_2 (the non-trivial first gap)
agg["gap_2"] = agg["lambda_3"] - agg["lambda_2"]

# Performance from compare.py CEC2017 D=10 mean @ 100K
perf = {
    1: (0,0), 2: (0,0), 3: (0,0), 4: (0,0),
    5: (2.263, 1.873), 6: (0.02869, 2.856e-7),
    7: (9.295, 12.16), 8: (1.580, 1.834),
    9: (0.06779, 0), 10: (86.08, 92.54),
    11: (0.4292, 0), 12: (120.1, 20.89),
    13: (2.701, 3.997), 14: (4.688, 0.5264),
    15: (1.279, 0.2138), 16: (1.547, 0.5760),
    17: (20.10, 1.998), 18: (18.12, 0.6503),
    19: (3.100, 0.02408), 20: (16.09, 1.334),
    21: (84.57, 100.3), 22: (24.00, 72.22),
    23: (259.3, 290.5), 24: (72.55, 102.2),
    25: (162.5, 228.2), 26: (166.7, 117.3),
    27: (381.8, 389.1), 28: (176.5, 252.9),
    29: (235.7, 231.5), 30: (419.2, 398.5),
}
floor = 1e-8
gap = {fn: np.log10(max(m, floor) / max(a, floor))
       for fn, (m, a) in perf.items()}
agg["log_gap"] = agg["fnum"].map(gap)

# Drop ties (both 0)
sub = agg.dropna(subset=["log_gap"])
sub = sub[~((sub["fnum"].isin([1,2,3,4]))) ]   # drop trivially-solved

print(f"N={len(sub)}")
for col in ["lambda_2", "lambda_3", "gap_2", "delta_star",
            "delta_star_norm", "phi_cheeger"]:
    r, p = spearmanr(sub[col], sub["log_gap"])
    print(f"  {col:20s}  rho = {r:+.3f}   p = {p:.3g}")
