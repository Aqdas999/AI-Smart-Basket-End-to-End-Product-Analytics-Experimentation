# PRD · Smart Basket: "Frequently bought together" at checkout

| | |
|---|---|
| **Status** | Tested (simulated A/B test complete): recommend rollout with holdout |
| **Product area** | Checkout / basket |
| **Platform context** | Olist, a Brazilian multi-seller e-commerce marketplace (2016–2018 public dataset) |
| **Related docs** | [Metrics definitions](02_Metrics_Definition.md) · [Metrics framework](03_Product_Metrics_Framework.md) · [Experiment design](04_Experiment_Design_and_Assumptions.md) · [Decision memo](05_Decision_Memo.md) |

> **Scope note.** This is a portfolio case study. The problem, the opportunity and the baseline numbers come from real Olist data. The experiment outcome is simulated, because the feature never existed. Everything here is written the way it would be for a real product team.

---

## 1. Problem

Olist grows by adding orders, not by growing baskets:

* **96.7% of orders contain a single product.** Only **3.3%** have two or more distinct products, and only **0.8%** span two categories.
* Average order value has been **flat at ~R$160** for 20 months while orders grew **185%** (H1 2018 vs H1 2017).
* **Only 3.0% of customers ever order twice.** Of those second orders, **31% happen on the same day** as the first: the customer comes back to buy something they could have added to the first basket.

Customers do want complementary items (people furnishing a bedroom buy bedding *and* décor), but the checkout gives them no help finding them. Every missed add-on is lost GMV, and sometimes a second shipment the customer pays for separately.

## 2. Opportunity

| | Value |
|---|---|
| AOV of single-product orders | R$157 |
| AOV of multi-product orders | R$244 (**+55%**) |
| Orders in the last 12 months | 75,343 |
| GMV per extra multi-product order | ≈ R$87 |
| **Value of +0.8 pp multi-product rate** | **≈ R$52k GMV / year (+0.4%)** |

The direct revenue prize is modest. The strategic prize is larger: basket-building is the behaviour that separates Olist's few repeat customers (avg lifetime GMV R$308) from one-time buyers (R$161).

## 3. Goals and non-goals

**Goals**
1. Increase the share of orders containing more than one product (**primary metric: multi-product order rate**).
2. Do it without hurting delivery experience, cancellations or review scores (**guardrails**).

**Non-goals (v1)**
* Personalised, product-level recommendations (v1 is category-level, to prove demand first).
* Recommendations outside checkout (home page, email).
* Changing pricing, shipping fees or seller ranking.

## 4. Target users

| Segment | Share of customers | Why it matters |
|---|---|---|
| New customers | ~97% | Almost all traffic; the first basket is the only chance to grow it |
| Home & living shoppers | ~21% of orders | Already 2× the average multi-product rate; natural complements |
| Returning customers | ~3% | Highest value, but too few to target alone in v1 |

## 5. Solution (v1)

A **"Customers also bought"** module in the cart and checkout, showing **3 recommendations**.

* **Logic:** category-affinity rules. For the main category in the cart, recommend the categories most often bought together with it (same order or same customer), ranked by co-purchase count, with a popularity fallback. See `src/smart_basket/recommender.py`.
* **Offline quality:** hit-rate@3 of **36.7% vs 31.1%** for a popularity baseline (+18% relative) on a time-based holdout.
* **Examples of learned rules:** bed/bath → home comfort (34× lift), toys ↔ baby, bed/bath ↔ furniture & décor.
* **One-tap add:** adding a recommendation keeps the customer in the checkout flow.

### User stories
* *As a shopper buying bedding*, I want to see matching décor items before I pay, so I don't have to search and check out twice.
* *As a shopper*, I want to dismiss the module easily, so it never slows down my purchase.
* *As the marketplace*, I want every recommendation logged (impression, click, add), so we can measure and improve the feature.

### Requirements
| # | Requirement | Priority |
|---|---|---|
| R1 | Show up to 3 recommendations based on the cart's primary category | Must |
| R2 | Popularity fallback when a category has no affinity rules | Must |
| R3 | Customer-level assignment via a stable hash (experiment flag) | Must |
| R4 | Log `impression`, `click`, `add_to_cart` events with variant and recommendation IDs | Must |
| R5 | Module fails silently (checkout unaffected if the recommender times out) | Must |
| R6 | Prefer in-stock items from the same seller as the cart (avoid split shipments) | Should (v2) |
| R7 | Price-aware ranking (avoid recommending items far cheaper than the cart) | Should (v2) |

## 6. Success metrics

| Type | Metric | Target / threshold |
|---|---|---|
| Primary | Multi-product order rate | ≥ +0.8 pp (pre-registered MDE) |
| Secondary | GMV per customer, AOV, items per order | Directionally positive |
| Guardrail | Cancellation rate | Must not rise > 0.3 pp |
| Guardrail | Review score | Must not fall > 0.05 |
| Guardrail | Late-delivery rate | Must not rise > 1 pp |
| Health | Widget CTR, add-to-cart rate after click | Monitored, no threshold |

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Items from another seller ship separately → late delivery, more freight, worse reviews | Delivery and review guardrails; v2 same-seller preference |
| Irrelevant recommendations feel spammy | Max 3 items, dismissible, ranked by co-purchase strength |
| Cheap add-ons raise conversion but barely move revenue | Track revenue per add; v2 price-aware ranking |
| Slows checkout | Async load, silent failure (R5); widget load rate monitored |

## 8. Launch plan

1. **A/B test** (11 weeks, 50/50, customer-level). ✅ Result: +1.38 pp, guardrails pass.
2. **Rollout to 90%** with a **10% long-term holdout** to measure revenue and repeat purchases.
3. **v2 experiment:** same-seller + price-aware ranking, primary metric revenue per exposed order.
