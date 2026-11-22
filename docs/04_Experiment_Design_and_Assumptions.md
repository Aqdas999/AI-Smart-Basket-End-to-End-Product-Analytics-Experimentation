# Experiment design & assumptions

Pre-registration document for the Smart Basket A/B test. Everything in sections 1–4 was fixed before any treatment data was examined. Analysis: [`notebooks/03_Smart_Basket_Experiment.ipynb`](../notebooks/03_Smart_Basket_Experiment.ipynb).

## 1. Hypothesis

Showing three "frequently bought together" category recommendations at checkout increases the share of orders that contain more than one distinct product.

* H₀: multi-product order rate (treatment) = multi-product order rate (control)
* H₁: they differ (two-sided test; we would want to know if the widget *hurt* baskets)

## 2. Design

| Parameter | Choice | Why |
|---|---|---|
| Unit of randomisation | Customer (`customer_unique_id`) | A customer must see a consistent experience across orders. Randomising orders would contaminate customers who buy twice. |
| Assignment | `md5("smart-basket-v1:" + customer_id)` → bucket in [0, 1); < 0.5 = treatment | Deterministic, stateless, reproducible, and independent across experiments (new salt per test) |
| Split | 50 / 50 | Maximum power for a fixed population |
| Population | All customers ordering between 5 Mar and 20 May 2018 | 11 full weeks (Mon–Sun), avoiding Black Friday / Christmas seasonality |
| Analysis | Intent-to-treat: every order by an assigned customer, including those where the widget failed to load and later-canceled orders | Avoids selection bias from conditioning on post-assignment behaviour |
| Variance | Delta method on customer-level sums (cross-checked with a 2,000-sample cluster bootstrap) | The metric is per order, but randomisation is per customer |

## 3. Metrics and thresholds

| Role | Metric | Decision threshold |
|---|---|---|
| Primary | Multi-product order rate | 95% CI excludes 0 |
| Secondary | AOV, GMV per customer, items per order | Holm-corrected, informative only |
| Guardrail | Cancellation rate | Upper 95% CI bound < +0.3 pp |
| Guardrail | Review score | Lower 95% CI bound > −0.05 |
| Guardrail | Late-delivery rate | Upper 95% CI bound < +1.0 pp |

**Decision rule:** **Ship** if the primary is significant and positive *and* all guardrails pass. **Iterate** if the primary is positive but not significant. **Stop** if the primary is negative or any guardrail fails.

## 4. Power analysis

| Input | Value |
|---|---|
| Baseline multi-product rate (8 weeks pre-test) | 2.83% |
| Minimum detectable effect | +0.8 pp absolute (+28% relative) |
| α (two-sided) / power | 0.05 / 0.80 |
| Required customers per arm | **7,668** |
| Customers per week (pre-test) | ~1,660 |
| Required duration | 10 weeks → **11 weeks planned** (whole weeks plus a buffer) |

**Why this MDE?** +0.8 pp ≈ R$52k GMV a year, the smallest effect worth the engineering and maintenance cost. Smaller effects would need over 6 months of traffic (MDE curve in the notebook).

**No peeking.** Results are read once, at the planned end date. Weekly charts are monitored for health only, not for stopping decisions.

## 5. Validity checks (all passed)

| Check | Result |
|---|---|
| 500 A/A tests on pre-period data | False-positive rate 5.6% (expected 5%); p-values uniform |
| Sample-ratio mismatch (χ²) | 9,063 vs 9,170 customers, p = 0.43 |
| One variant per customer | ✅ |
| Control never exposed (0 impressions, 0 clicks) | ✅ |
| Pre-treatment covariate balance (basket value, returning share, category mix, state) | No significant differences (smallest p = 0.15) |

## 6. Simulation assumptions

**Why simulate:** Olist never launched this feature, so the counterfactual can't be observed. The notebook replays real orders: **control = exactly what happened**, and **treatment = the same real orders plus simulated widget behaviour.**

| Parameter | Value | Basis |
|---|---|---|
| Widget load rate | 98% | Typical client-side module reliability |
| CTR when a recommendation matches a category the customer really bought in another order | 20% | Relevant recommendations get clicked several times more often |
| CTR otherwise | 5% | Typical e-commerce recommendation-widget CTR (low single digits to ~10%) |
| Add-to-basket rate after a click | 25% | Typical product-page add-to-cart rate |
| Added item price and freight | Random real order line from the recommended category, training period | Keeps basket values realistic |
| Effect on cancellations, reviews, delivery | **None modelled** | These are real outcomes; guardrails therefore measure noise only here |
| Random seed | 42 | Reproducible |

**Built-in correctness check:** with these parameters the expected (true) lift is **+1.21 pp**. The analysis estimates **+1.38 pp, 95% CI [+0.82, +1.94]**, so the truth lies inside the interval.

### What the simulation can't tell us
* The real CTR or add rate (these are assumptions).
* Whether the widget distracts customers and *lowers* checkout completion (Olist has no session or funnel data).
* Long-term effects on repeat purchasing.
* Real guardrail harm from split shipments.

A live test would measure all of these. The design, checks and analysis would stay exactly the same.

## 7. Results summary

| | Control | Treatment | Difference | 95% CI | p |
|---|---|---|---|---|---|
| **Multi-product order rate** | 3.25% | 4.63% | **+1.38 pp (+42%)** | [+0.82, +1.94] pp | 1.5 × 10⁻⁶ |
| AOV | R$162.69 | R$168.54 | +3.6% | [−R$0.41, +R$12.11] | 0.12 (Holm) |
| GMV per customer | R$164.72 | R$170.85 | +3.7% | [−R$0.23, +R$12.50] | 0.12 (Holm) |
| Items per order | 1.147 | 1.167 | +1.7% | [+0.003, +0.037] | 0.056 (Holm) |
| Cancellation rate | 0.20% | 0.27% | +0.07 pp | [−0.07, +0.21] pp | PASS |
| Review score | 4.044 | 4.045 | +0.001 | [−0.039, +0.041] | PASS |
| Late-delivery rate | 9.97% | 9.63% | −0.33 pp | [−1.20, +0.54] pp | PASS |

**Funnel (treatment):** 9,296 orders → 9,113 impressions (98.0%) → 480 clicks (5.3% CTR) → 112 items added (23.3% of clicks).

**Revenue caution:** treatment baskets were already 2.8% larger *before* any simulated behaviour (random chance, p = 0.15). Of the +R$5.85 AOV gap, about R$4.59 is that pre-existing difference, and only **R$1.25 per order (+0.8%)** came from added items. That's far below the ±R$6 noise. The test cannot, and does not claim to, show a revenue lift.

**Decision: SHIP** under the pre-registered rule, with a 10% holdout to measure revenue and repeat purchasing.
