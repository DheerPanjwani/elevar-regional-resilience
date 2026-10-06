# paper figures 3, 5 and 6, rebuilt at 300 dpi from data/processed alone.
# figures 1, 2 and 4 need the raw panels and the district boundaries, so they stay in NB6.
# usage: python scripts/figures_from_processed.py  (writes to figures/)

import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

path, out = "data/processed", "figures"
os.makedirs(out, exist_ok=True)

NAVY, LIGHT, ACC, GREY = "#1F3864", "#B4C6E7", "#C0504D", "#595959"
mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GREY,
    "axes.labelcolor": "black", "axes.titlesize": 9.5, "axes.titleweight": "bold",
    "xtick.color": GREY, "ytick.color": GREY, "axes.spines.top": False,
    "axes.spines.right": False, "savefig.dpi": 300, "savefig.bbox": "tight",
    "legend.frameon": False,
})

W = pd.read_parquet(f"{path}/shock_matrix.parquet")
W.columns = W.columns.astype(int)
L = pd.read_parquet(f"{path}/factor_loadings.parquet").set_index("Dist Code")
S = pd.read_parquet(f"{path}/systematic_share.parquet").set_index("Dist Code")
sd_all = W.std().mean()
rng = np.random.default_rng(2026)

# ---- figure 3: risk composition by consumption quintile ----
D = S.dropna(subset=["r2_sys", "region", "secc_cons_pc_rural"]).copy()
D["sys_sd"] = np.sqrt((D.tot_sd ** 2 - D.idio_sd ** 2).clip(lower=0))
D["q"] = pd.qcut(D.secc_cons_pc_rural, 5, labels=["Q1\npoorest", "Q2", "Q3", "Q4", "Q5\nrichest"])
Q = D.groupby("q", observed=True)[["sys_sd", "idio_sd", "tot_sd", "r2_sys", "beta"]].mean()
x = np.arange(5)

fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(9.8, 3.3))
a1.bar(x, Q.idio_sd ** 2, 0.62, color=LIGHT, label="district-specific")
a1.bar(x, Q.sys_sd ** 2, 0.62, bottom=Q.idio_sd ** 2, color=NAVY, label="common factor")
a1.set_ylabel("Variance of output shock")
a1.set_title("Total risk by quintile", loc="left")
a1.set_ylim(0, (Q.tot_sd ** 2).max() * 1.3)
a1.legend(fontsize=7.5, loc="upper right")
a2.bar(x, Q.r2_sys * 100, 0.62, color=NAVY)
for i, v in enumerate(Q.r2_sys * 100):
    a2.text(i, v + 0.6, f"{v:.0f}%", ha="center", fontsize=7.5)
a2.set_ylabel("Systematic share of risk (%)")
a2.set_title("Share from the monsoon factor", loc="left")
a3.plot(x, Q.beta, "o-", color=ACC, lw=2, ms=6)
a3.set_ylim(0, Q.beta.max() * 1.25)
a3.set_ylabel("Beta on the monsoon factor")
a3.set_title("Beta", loc="left")
for a in (a1, a2, a3):
    a.set_xticks(x)
    a.set_xticklabels(Q.index)
fig.tight_layout()
fig.savefig(f"{out}/fig3_decorrelation.png")
plt.close(fig)

# ---- figure 5: effective diversification ----
ks = [1, 2, 3, 5, 8, 12, 20, 30, 50, 80, 120, 150]
port = [np.mean([W[rng.choice(W.columns, k, replace=False)].mean(axis=1).std() for _ in range(1000)]) for k in ks]
keff = [(sd_all / p) ** 2 for p in port]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.4, 3.4))
a1.plot(ks, [sd_all / np.sqrt(k) for k in ks], "--", color=GREY, lw=1.6, label="if districts were independent")
a1.plot(ks, port, "-o", color=NAVY, lw=2, ms=4, label="actual")
a1.axhline(port[-1], color=ACC, lw=1, ls=":")
a1.text(1.1, port[-1] * 0.88, f"floor ≈ {port[-1]:.2f}", color=ACC, fontsize=8)
a1.set_xscale("log")
a1.set_xlabel("Districts held")
a1.set_ylabel("Portfolio standard deviation")
a1.legend(fontsize=8)
a2.plot(ks, ks, "--", color=GREY, lw=1.6, label="nominal")
a2.plot(ks, keff, "-o", color=NAVY, lw=2, ms=4, label="effective")
a2.set_xscale("log")
a2.set_yscale("log")
a2.set_xlabel("Districts held")
a2.set_ylabel("Effective positions")
a2.legend(fontsize=8)
fig.tight_layout()
fig.savefig(f"{out}/fig5_diversification.png")
plt.close(fig)

# ---- figure 6: correlation effect against volatility selection ----
def levers(cols):
    port_sd = W[cols].mean(axis=1).std()
    ind_sd = W[cols].std().mean()
    return (ind_sd / port_sd) ** 2, (sd_all / ind_sd) ** 2


def region_book(n=20):
    regions = L.region.unique()
    picked = []
    for i in range(n):
        pool = [c for c in L[L.region == regions[i % 6]].index if c not in picked]
        picked.append(rng.choice(pool))
    return picked


pts = {s + " (20)": levers(L[L["State Name"] == s].index.tolist()[:20])
       for s in ["Rajasthan", "Madhya Pradesh", "Maharashtra", "Uttar Pradesh"]}
pts["All 214 districts"] = levers(list(W.columns))
draws = np.array([levers(region_book()) for _ in range(2000)])

fig, ax = plt.subplots(figsize=(6.8, 4.3))
ax.axvspan(1.4, 2.4, color="#F2F2F2", zorder=0)
ax.axhline(1, lw=0.7, color=GREY, ls=":")
m = draws.mean(axis=0)
lo, hi = np.percentile(draws, 5, axis=0), np.percentile(draws, 95, axis=0)
ax.errorbar(m[0], m[1], xerr=[[m[0] - lo[0]], [hi[0] - m[0]]], yerr=[[m[1] - lo[1]], [hi[1] - m[1]]],
            fmt="o", ms=9, color=ACC, ecolor=ACC, elinewidth=1, capsize=3, zorder=3)
ax.annotate("Spread across 6 regions (20)\nmean and 5th–95th pct of 2,000 draws",
            (m[0], m[1]), textcoords="offset points", xytext=(12, 8), fontsize=8)
offsets = {"Rajasthan (20)": (10, -4), "Madhya Pradesh (20)": (10, -12), "Maharashtra (20)": (10, 6),
           "Uttar Pradesh (20)": (10, -4), "All 214 districts": (10, -12)}
for lab, (k, v) in pts.items():
    ax.scatter(k, v, s=80, color=NAVY, edgecolor="white", lw=1.2, zorder=3)
    ax.annotate(lab, (k, v), textcoords="offset points", xytext=offsets[lab], fontsize=8)
ax.text(1.9, 2.95, "single-state books", ha="center", fontsize=8, color=GREY, style="italic")
ax.set_xlim(0, 9.5)
ax.set_ylim(0, 3.1)
ax.set_xlabel("Correlation effect  →  spread across risk regions")
ax.set_ylabel("Volatility selection  →  calmer districts")
fig.savefig(f"{out}/fig6_two_levers.png")
plt.close(fig)
print("written to", out)
