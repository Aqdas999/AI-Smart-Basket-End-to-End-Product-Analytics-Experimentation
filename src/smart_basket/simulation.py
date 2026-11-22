"""Simulates the Smart Basket A/B test on top of real Olist orders.

Why simulate? Olist never shipped this feature, so historical data cannot
show what treatment customers *would* have done. This module keeps every
control order exactly as it happened and, for treatment customers, layers
the widget's behaviour on top of their real order:

    impression  ->  click  ->  add recommended item to the basket

Clicks can only happen when the widget is shown (treatment only), and adds
can only happen after a click. The probability of a click is higher when a
recommendation matches a category the customer really bought in another
order, which ties the simulated effect to the recommender's real quality.

All behavioural parameters live in ``SimulationParams`` and are documented
in docs/04_Experiment_Design_and_Assumptions.md. The true effect is
therefore *known*, which lets us check that the analysis recovers it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .recommender import CategoryAffinityRecommender


@dataclass(frozen=True)
class SimulationParams:
    widget_load_rate: float = 0.98        # widget fails to render ~2% of the time
    p_click_relevant: float = 0.20        # a recommended category matches real interest
    p_click_other: float = 0.05           # typical recommendation-widget CTR
    p_add_given_click: float = 0.25       # clicks that end with an item in the basket
    seed: int = 42

    def to_dict(self) -> dict:
        return asdict(self)


def customer_interests(exp_orders: pd.DataFrame, all_orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.Series:
    """For every experiment order, the categories its customer bought in their
    *other* orders across the full history — a proxy for real latent interest.

    (A category that also appears in the experiment order itself is excluded,
    because the customer already has it in the basket.)
    """
    lines = order_items.merge(all_orders[["order_id", "customer_unique_id"]], on="order_id")
    by_customer = lines.groupby("customer_unique_id")["category"].apply(set)
    by_order = lines.groupby("order_id")["category"].apply(set)
    cust = exp_orders.set_index("order_id")["customer_unique_id"]
    return pd.Series(
        {oid: by_customer.get(cust[oid], set()) - by_order.get(oid, set()) for oid in exp_orders["order_id"]}
    )


def simulate(
    exp_orders: pd.DataFrame,
    interests: pd.Series,
    catalogue_lines: pd.DataFrame,
    model: CategoryAffinityRecommender,
    params: SimulationParams = SimulationParams(),
) -> pd.DataFrame:
    """Return ``exp_orders`` with simulated widget events and post-feature outcomes.

    ``exp_orders`` must already carry a ``variant`` column.
    ``catalogue_lines`` (training-period order lines) supplies realistic price
    and freight for any item a customer adds.
    """
    rng = np.random.default_rng(params.seed)
    df = exp_orders.copy()
    n = len(df)
    is_t = (df["variant"] == "treatment").to_numpy()

    recs = df["primary_category"].map(lambda c: model.recommend(c, 3))
    interest = df["order_id"].map(interests).apply(lambda s: s if isinstance(s, set) else set())
    relevant_cats = [[c for c in r if c in i] for r, i in zip(recs, interest)]
    relevant = np.array([len(x) > 0 for x in relevant_cats])

    impression = is_t & (rng.random(n) < params.widget_load_rate)
    p_click = np.where(relevant, params.p_click_relevant, params.p_click_other)
    click = impression & (rng.random(n) < p_click)
    added = click & (rng.random(n) < params.p_add_given_click)

    # what gets added: a relevant category if there is one, else a random recommendation
    price_pool = {c: g[["price", "freight_value"]].to_numpy() for c, g in catalogue_lines.groupby("category")}
    add_price = np.zeros(n)
    add_freight = np.zeros(n)
    add_cat = np.array([None] * n, dtype=object)
    for i in np.flatnonzero(added):
        cat = relevant_cats[i][0] if relevant_cats[i] else recs.iloc[i][rng.integers(0, len(recs.iloc[i]))]
        pool = price_pool.get(cat)
        if pool is None:
            continue
        price, freight = pool[rng.integers(0, len(pool))]
        add_cat[i], add_price[i], add_freight[i] = cat, price, freight

    df["recommendations"] = recs.str.join(", ")
    df["recommendation_relevant"] = relevant
    df["impression"] = impression
    df["clicked"] = click
    df["added_recommendation"] = added
    df["added_category"] = add_cat
    df["added_item_revenue"] = add_price
    df["added_freight"] = add_freight

    # post-feature outcomes (control orders are unchanged)
    df["items_count"] = df["items_count"] + added.astype(int)
    df["distinct_products"] = df["distinct_products"] + added.astype(int)
    df["is_multi_product"] = df["distinct_products"] > 1
    df["item_revenue"] = df["item_revenue"] + add_price
    df["freight_revenue"] = df["freight_revenue"] + add_freight
    df["gmv"] = df["item_revenue"] + df["freight_revenue"]
    return df
