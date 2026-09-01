# NFP Forecast — July 2026 (release Fri Aug 7 2026)

Generated: 2026-09-01T15:55:36

## Final blended forecast

**+88K jobs**  (68% CI [+57, +119])

Directional lean: **IN LINE WITH consensus** (+3K deviation)

## Components

| Component | Point | RMSE |
|---|---|---|
| ML ensemble (9 models) | +83K | 126K |
| Bridge models (median of 32) | +116K | ~110K |
| All-models grand median | +111K | dispersion 43K |
| Consensus (Bloomberg pre-ADP) | +85K | 55K |
| **Blended (Bayesian)** | **+88K** | **31K** |

## Known inputs used

- ADP Jul: +68K (miss -30K)
- Jobless claims 4wk: ~203K (low)
- ISM Mfg Employment: 52.8 (+3.1 breakout)
- Empire/Philly Fed employment: positive
- UMich Sentiment: 55.2 (5mo high)
- Challenger cuts: 62,075 (+140% YoY)

## All model predictions

```
         model  prediction_k        MAE
 Naive: 3m avg    111.333333  91.694444
Naive: 12m avg     49.833333 104.916667
           OLS     76.548158 101.256324
    Ridge(1.0)     80.161055  92.872207
     Ridge(10)     91.453563  95.489450
  ElasticNetCV     93.483400  95.757140
    RF(300,d6)     83.771206  93.843457
   GBM(200,d3)     62.924805 103.991817
   XGB(300,d4)     95.186638  93.917676
```

### Bridge models

```
b_kitchen_post_covid              +65.7K
b_leading_5_post_covid            +71.1K
b_leading_5_2010+                 +71.1K
b_5var_post_covid                 +73.1K
b_kitchen_2010+                   +77.9K
b_vintage_jolts_2010+             +82.5K
b_refwk_adp_2010+                 +89.5K
b_ism_adp_post_covid              +91.9K
b_ism_adp_2010+                   +91.9K
b_adp_only_post_covid             +94.2K
b_adp_claims_2010+                +96.3K
b_ar_ext_2010+                    +96.4K
b_5var_2010+                     +102.5K
b_adp_ar_post_covid              +102.7K
b_vintage_full_2010+             +106.6K
b_adp_claims_emp_2010+           +113.9K
b_ar_post_covid                  +117.3K
b_vintage_jolts_post_covid       +121.1K
b_adp_ar_2010+                   +124.0K
b_vintage_full_post_covid        +131.9K
b_ar_2010+                       +134.0K
b_adp_only_2010+                 +136.1K
b_ar_ext_post_covid              +137.2K
b_adp_claims_emp_post_covid      +152.8K
b_adp_claims_post_covid          +159.3K
b_refwk_ism_post_covid           +177.8K
b_refwk_ism_2010+                +177.8K
b_supertight_post_covid          +178.9K
b_supertight_2010+               +178.9K
b_refwk_only_2010+               +179.2K
b_refwk_adp_post_covid           +206.6K
b_refwk_only_post_covid          +259.1K
```
