# how much diversification does a twenty-district book spread across the six risk regions buy?
# averages the NB5 cell 6 decomposition over many random draws instead of relying on one draw.
# runs on data/processed alone:  python scripts/region_spread_check.py

import numpy as np
import pandas as pd

path = "data/processed"
W = pd.read_parquet(f"{path}/shock_matrix.parquet")
W.columns = W.columns.astype(int)
L = pd.read_parquet(f"{path}/factor_loadings.parquet").set_index("Dist Code")
sd_all = W.std().mean()


def levers(cols):
    port_sd = W[cols].mean(axis=1).std()
    ind_sd = W[cols].std().mean()
    return (ind_sd / port_sd) ** 2, (sd_all / ind_sd) ** 2, ind_sd


def region_book(rng, n=20):
    regions = L.region.unique()
    picked = []
    for i in range(n):
        pool = [c for c in L[L.region == regions[i % 6]].index if c not in picked]
        picked.append(rng.choice(pool))
    return picked


rng = np.random.default_rng(2026)
spread = np.array([levers(region_book(rng)) for _ in range(2000)])
rand = np.array([levers(list(rng.choice(W.columns, 20, replace=False))) for _ in range(2000)])

print("twenty districts, 2,000 draws each")
for name, x in [("spread across six regions", spread), ("random", rand)]:
    print(f"  {name:26s} correlation effect {x[:,0].mean():.1f} "
          f"(5th-95th {np.percentile(x[:,0],5):.1f}-{np.percentile(x[:,0],95):.1f}), "
          f"volatility selection x{x[:,1].mean():.2f}, mean individual sd {x[:,2].mean():.3f}")

print("\nsingle-state books (first twenty districts by code, as in NB5)")
for s in ["Rajasthan", "Madhya Pradesh", "Maharashtra", "Uttar Pradesh"]:
    k, v, sd = levers(L[L["State Name"] == s].index.tolist()[:20])
    print(f"  {s:16s} correlation effect {k:.1f}, volatility selection x{v:.2f}")
