# Regional Resilience and Demand-Risk Framework for Rural India

Research project completed at Elevar Equity in 2026 by Dheer Panjwani. It asks how badly a failed monsoon hits each rural district in India, and what that means for a lender or investor deciding where to spread a portfolio.

The short answer has two parts. First, district exposure to drought is measurable and fairly stable, and a simple fragility score built on it lines up with rural poverty. Second, and more useful for portfolio construction, weather shocks across India are far more correlated than a district count suggests. A 150-district book behaves like about six and a half independent bets, and a single-state book like fewer than two. Shocks are also much more correlated in poorer districts, so lenders concentrated there get less diversification than they think.

## Headline results

| Result | Number | Where |
| --- | --- | --- |
| Output falls with rainfall shortfall, not with surplus | β⁻ = 0.141 (t 8.5); β⁺ = 0.000 (t 0.0); N = 14,115 district-years | NB1 |
| District exposure is reliably estimated | Empirical Bayes reliability 0.92 across 268 districts | NB1 |
| Structural features predict exposure moderately | Out-of-fold R² 0.50 (boosted, ICRISAT ∪ SHRUG) | NB1, NB3 |
| Exposure has fallen over fifty years | Mean 0.253 → 0.196 (t −2.72); 157 of 248 districts improved | NB2 |
| Shocks share one national component | PC1 explains 16.9%; corr(PC1, national rainfall) = 0.81; six regions explain 53.5% | NB5 |
| Effective diversification is low | 150 districts ≈ 6.5 independent bets; one state 1.7–2.1; six-region spread 7.0 | NB5 |
| Poorer districts have more systematic shocks | Systematic share 29.7% (poorest quintile) to 8.0% (richest); region FE t −4.89, state FE t −2.04 | NB5 |
| A book confined to the poorest 40% of districts diversifies poorly | 81 districts ≈ 4.0 independent bets, against 6.7 for 81 districts drawn from the rest | NB5 cell 12 |

Five candidate buffers came back null or uninterpretable: tertiary GDP share, agricultural wages, night lights, non-farm employment in the SHAP ranking, and total-GDP interactions (an accounting identity). These are reported in the paper because they narrow down where the buffering mechanism sits: below the district, at household and village level.

## The resilience score

```
Fragility_d  = Exposure_d × PrimaryShare_d
Resilience_d = 100 − percentile(Fragility_d)
```

Exposure is the district's estimated output loss per standard deviation of kharif rainfall shortfall. Primary share is agriculture's share of district GDP. A district scores low when a failed monsoon cuts deep into farm output and farming is a large part of the local economy. The score is estimated on all districts in the panel; income is used to validate it and to sort districts, not as an input.

The least resilient third of districts has 33.0% rural poverty (SECC 2011), against 23.1% in the most resilient third. Resilience predicts poverty across India (t −4.15) and within regions (t −3.42), but not within states (t −1.12).

## The poorest 40% of districts

NB5 cell 12 treats the bottom two quintiles of districts by SECC rural consumption per capita (81 districts, 44% average rural poverty against 20% elsewhere) as a lending universe of their own. Their drought exposure is about the same as everyone else's (0.241 against 0.234), but their shocks move together far more: 25% of shock variance is driven by the national monsoon factor, against 13% in the other 60%. The gap holds with region fixed effects (t 2.71) and state fixed effects (t 2.04). As a result, an equal-weight book across all 81 behaves like about 4 independent bets, while 81 districts drawn at random from the richer 60% give 6.7 (5th–95th percentile 5.7–7.9).

For a lender whose mandate is the poorest districts, spreading the book wider buys less protection than the district count suggests. The quintiles are of districts by average consumption, not of households by income.

## Repository layout

```
notebooks/
  NB1.ipynb   Core build: rainfall shocks, asymmetric exposure, EB shrinkage, structural model + SHAP, resilience score, map export
  NB2.ipynb   H1: fifty-year change in exposure; diagnosis and rebuild of the broken non-farm share column
  NB3.ipynb   SHRUG: night lights as a demand proxy (null), SHRUG district features, refit of exposure model
  NB4.ipynb   Groundwater depletion vs exposure change (Fisher test, not significant)
  NB5.ipynb   Factor structure, risk regions, portfolio overlays, effective diversification, consumption quintiles, poorest-40% book
  NB6.ipynb   Publication figures
data/
  processed/  Small district-level outputs (parquet); enough to run NB5 cell 12 and the factor tables without the raw panels
  README.md   Raw data sources and how to rebuild
```

The paper, presentation and research note on credit cycles are in this folder: DRIVE_LINK

## Reproducing

The notebooks were written for Google Colab and read raw data from `/content/drive/My Drive/Data/Elevar`. To rerun them, put the raw files listed in `data/README.md` in that folder (or change the `BASE` path at the top of each notebook) and run NB1 through NB6 in order. Python dependencies are in `requirements.txt`. NB5 cell 12 runs on the files in `data/processed` alone if you point `BASE` there.

## Known issues

- **Hover labels on the resilience map** (NB1 cells 9–10) still show the original ICRISAT `nonfarm_worker_share`, which NB2 shows is broken. The corrected Census-based share should replace it before the map is shared again. The buffer index in NB1 also uses the broken column.
- **Tamil Nadu** is measured on kharif (southwest monsoon) rainfall only. Most of its rain comes from the northeast monsoon, so its exposure figures are understated or noisy.
- **Palghar** was carved out of Thane in 2014. All district data for the Palghar corridor are for undivided Thane, which is dominated by the Thane–Kalyan–Bhiwandi urban belt.
- **Chittoor** is an Andhra Pradesh district and loads on region F3, not F5. Its shock correlation with the Palghar corridor is +0.24, so the two fieldwork corridors are not a diversified pair.
- Portfolio footprints in NB5 are reconstructed from public sources with equal or assumed weights, not from the companies' own branch data.
- Region fixed-effect regressions in NB5 cluster on six regions, which is too few clusters for reliable standard errors; the state-clustered versions are the safer read.

## Fieldwork

Household interviews were carried out in Palghar (Maharashtra, 18 households) and Chittoor (Andhra Pradesh, 9 households) in 2026. The notes, audio and photographs are not in this repository.
