# NFP Forecast — July 2026 (release Fri Aug 7 2026)

Generated: 2026-09-02T10:50:45

## Final blended forecast

**+90K jobs**  (68% CI [+59, +121])

Directional lean: **IN LINE WITH consensus** (+5K deviation)

## Components

| Component | Point | RMSE |
|---|---|---|
| ML ensemble (9 models) | +20K | 126K |
| Bridge models (median of 20) | +109K | ~110K |
| All-models grand median | +94K | dispersion 62K |
| Consensus (Bloomberg pre-ADP) | +85K | 55K |
| **Blended (Bayesian)** | **+90K** | **31K** |

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
 Naive: 3m avg     20.000000  91.694444
Naive: 12m avg     38.250000 104.916667
           OLS     -4.466077 101.256324
    Ridge(1.0)      3.294977  92.872207
     Ridge(10)     28.958989  95.489450
  ElasticNetCV     67.978959  95.757140
    RF(300,d6)     17.211667  93.843457
   GBM(200,d3)    -10.605897 103.991817
```

### Bridge models

```
b_kitchen_post_covid              +36.5K
b_ar_post_covid                   +39.8K
b_adp_ar_post_covid               +46.8K
b_ar_2010+                        +67.5K
b_adp_ar_2010+                    +67.7K
b_5var_post_covid                 +87.7K
b_adp_only_post_covid             +89.0K
b_refwk_adp_2010+                 +94.2K
b_kitchen_2010+                   +94.4K
b_adp_claims_2010+                +94.5K
b_refwk_adp_post_covid           +122.8K
b_ar_ext_post_covid              +133.2K
b_adp_only_2010+                 +133.9K
b_adp_claims_post_covid          +134.5K
b_ar_ext_2010+                   +139.6K
b_5var_2010+                     +151.4K
b_adp_claims_emp_post_covid      +160.2K
b_refwk_only_post_covid          +171.7K
b_refwk_only_2010+               +181.2K
b_adp_claims_emp_2010+           +193.4K
```
