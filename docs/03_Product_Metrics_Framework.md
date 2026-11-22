# Product metrics framework

How the metrics in this project fit together, and why Smart Basket targets the lever it does.

## North Star

**Monthly GMV from valid orders.** It captures value created for buyers and sellers, and for a marketplace that monetises on commission it is the closest proxy for revenue.

## Metric tree

```text
                         Monthly GMV
                              │
          ┌───────────────────┴───────────────────┐
     Orders / month                           AOV  (flat ~R$160)
          │                                        │
   ┌──────┴───────┐                    ┌───────────┴────────────┐
 New customers   Repeat orders     Items per order          Price per item
 (≈97%)          (3% repeat rate)   (1.14)                   (category mix)
                      │                  │
                      │          Multi-product order rate (3.3%)  ◄── Smart Basket
                      │                  │
                      └──── basket-building habit ────┘
                                         │
                 Guardrails: late-delivery rate · review score · cancellation rate
```

## Where the growth has come from

| Lever | What the data shows | Status |
|---|---|---|
| New customers | Orders +185% H1 2018 vs H1 2017 | Main growth engine, dependent on acquisition spend |
| Repeat orders | 3.0% repeat rate, ~5.7% of GMV | Structurally weak |
| Items per order | 1.14; only 3.3% of orders multi-product | **Untapped** |
| Price per item | AOV flat for 20 months | Stable |

**Why basket size?** It's the only lever that grows GMV from traffic Olist already paid for. Multi-product orders are worth 55% more, and 31% of second orders happen the same day as the first, so the demand already exists.

## Input metrics → outcome metrics

| Layer | Metric | Moved by | Read when |
|---|---|---|---|
| **Health (input)** | Widget CTR, add rate | Recommendation quality, UI | Daily |
| **Primary (behaviour)** | Multi-product order rate | Smart Basket | End of test |
| **Outcome** | AOV, GMV per customer | Basket size × item price | Holdout, monthly |
| **Long-term** | Repeat-customer rate, lifetime GMV | Habit, satisfaction | Holdout, quarterly |
| **Guardrail** | Late delivery, review score, cancellations | Split shipments, bad recs | End of test + monitoring |

**Why not use revenue as the primary metric?** Order values are heavily skewed (mean R$160, median R$105), so revenue metrics need many times more traffic to detect the same effect. In the experiment, revenue per order rose by a true ~R$1.25, while the noise was ±R$6. A behavioural primary metric that sits directly on the causal path is detectable. Revenue is then confirmed over a longer period through a holdout.

## Segments that matter

| Segment | Multi-product rate | Implication |
|---|---|---|
| Bed/bath/table | 7.6% | Strong natural complements, so the best first surface |
| Furniture & décor | 5.1% | Same |
| Electronics | 0.8% | Few complements, so expect low engagement |
| Health & beauty (largest category by GMV) | 2.3% | Big volume, average affinity |

## Review cadence

| Cadence | What |
|---|---|
| Daily | Widget load rate, CTR, errors (health) |
| Weekly | Primary metric by variant (no peeking decisions), guardrails |
| End of test | Full readout against the pre-registered decision rule |
| Monthly / quarterly | Holdout: GMV per customer, repeat rate |
