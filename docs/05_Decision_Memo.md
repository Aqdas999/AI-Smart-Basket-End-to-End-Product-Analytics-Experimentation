# Decision memo · Smart Basket A/B test

**To:** Head of Product, Checkout · **From:** Product Analytics · **Re:** Launch decision for Smart Basket v1

## Recommendation

**Roll Smart Basket out to 90% of customers and keep a 10% holdout for at least one quarter.**

## Why

1. **It works on the behaviour it targets.** The multi-product order rate rose from **3.25% to 4.63%** (+1.38 pp, +42%, 95% CI +0.82 to +1.94 pp). The lift held in 10 of 11 weeks with no novelty decay, and appeared for both new customers and every category group tested.
2. **It did no harm.** Cancellations, review scores and late deliveries all stayed within their pre-agreed limits.
3. **The result is trustworthy.** Assignment was balanced (no sample-ratio mismatch), 500 A/A tests produced the expected 5% false-positive rate, and the analysis recovered the known simulated effect.

## What we can't claim yet

**Revenue.** The added items are worth about **R$1.25 per order (+0.8%)**, well below what an 11-week test can detect (±R$6). AOV looks 3.6% higher in treatment, but most of that gap existed before the feature did anything (the treatment group happened to have slightly bigger baskets). **We should not report a revenue lift from this test.**

The holdout closes this gap: three more months of data will measure revenue per customer and, more importantly, whether basket-building customers come back more often (today only 3% do).

## Next steps

| # | Action | Owner | When |
|---|---|---|---|
| 1 | Ramp to 90% with 10% holdout; daily health monitoring (load rate, CTR) | Eng + Analytics | Week 1 |
| 2 | v2: prefer items from the **same seller** (no extra shipment) and **price-aware** ranking (raise value per add) | Product + Data Science | Next quarter |
| 3 | v2 test with **revenue per exposed order** as primary metric, sized for that metric's higher variance | Analytics | After v2 build |
| 4 | Holdout readout: GMV per customer, 90-day repeat rate | Analytics | +1 quarter |

## Context for the reader

* Olist sells across 74 categories; **96.7%** of orders are a single product, and AOV has been flat at ~R$160 while orders grew 185% (H1 2018 vs H1 2017).
* **31% of second orders are placed the same day as the first.** Customers want more items; checkout makes them come back for them.
* The experiment is a **simulation on real order data** (Olist never shipped this feature). Behavioural assumptions are documented in [`04_Experiment_Design_and_Assumptions.md`](04_Experiment_Design_and_Assumptions.md).
