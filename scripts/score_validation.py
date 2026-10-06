# does the resilience score line up with rural poverty?  terciles and three regressions.
# uses outputs/district_scores.csv (all 268 scored districts) and the SECC poverty rate in
# data/processed, which covers the 214-district balanced panel, so N here is about 203.
# usage: python scripts/score_validation.py

import pandas as pd
import statsmodels.api as sm

scores = pd.read_csv("outputs/district_scores.csv").set_index("dist_code")
S = pd.read_parquet("data/processed/systematic_share.parquet").set_index("Dist Code")
scores["tercile"] = pd.qcut(scores.resilience, 3, labels=["least resilient", "middle", "most resilient"])

D = scores.join(S[["secc_pov_rate_rural", "cultiv_sh", "st_sh", "literacy2", "primary_share"]]).dropna(subset=["secc_pov_rate_rural"])
print(f"districts with SECC poverty: {len(D)} of {len(scores)}\n")
print(D.groupby("tercile", observed=True)[["secc_pov_rate_rural", "cultiv_sh", "st_sh", "literacy2", "primary_share"]].mean().round(3).to_string())

z = (D.resilience - D.resilience.mean()) / D.resilience.std()
print("\nrural poverty on standardised resilience")
for fe in [None, "risk_region", "state"]:
    X = pd.DataFrame({"resilience": z})
    if fe:
        X = pd.concat([X, pd.get_dummies(D[fe], drop_first=True, dtype=float)], axis=1)
        fit = sm.OLS(D.secc_pov_rate_rural, sm.add_constant(X)).fit(cov_type="cluster", cov_kwds={"groups": D[fe]})
    else:
        fit = sm.OLS(D.secc_pov_rate_rural, sm.add_constant(X)).fit(cov_type="HC1")
    print(f"  {fe or 'no fixed effects':16s} {fit.params['resilience']:+.4f} (t {fit.tvalues['resilience']:.2f})")
