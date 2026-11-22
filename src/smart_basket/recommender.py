"""Smart Basket v1: a category-affinity recommender.

Deliberately simple and explainable (no black-box model): for the category a
customer is buying, recommend the categories most often bought *together with
it* — in the same order or by the same customer — in the training period.
Ties and cold-start categories fall back to overall popularity.

Evaluated offline with a time split (train before the cutoff, test after) and
compared against a popularity baseline using hit-rate@k.
"""

from __future__ import annotations

from itertools import permutations

import pandas as pd


def _basket_pairs(lines: pd.DataFrame, key: str) -> pd.DataFrame:
    baskets = lines.groupby(key)["category"].apply(lambda s: sorted(set(s)))
    baskets = baskets[baskets.str.len() > 1]
    rows = [pair for cats in baskets for pair in permutations(cats, 2)]
    return pd.DataFrame(rows, columns=["anchor", "recommended"])


def co_purchase_table(lines: pd.DataFrame) -> pd.DataFrame:
    """Directed category co-purchase counts with confidence and lift.

    ``lines`` needs columns: order_id, customer_unique_id, category.
    """
    pairs = pd.concat(
        [_basket_pairs(lines, "order_id"), _basket_pairs(lines, "customer_unique_id")],
        ignore_index=True,
    )
    co = pairs.value_counts().rename("co_purchases").reset_index()
    popularity = lines["category"].value_counts(normalize=True)
    co["confidence"] = co["co_purchases"] / co.groupby("anchor")["co_purchases"].transform("sum")
    co["lift"] = co["confidence"] / co["recommended"].map(popularity)
    return co.sort_values(["anchor", "co_purchases"], ascending=[True, False]).reset_index(drop=True)


class CategoryAffinityRecommender:
    def __init__(self, k: int = 3, min_co_purchases: int = 2):
        self.k = k
        self.min_co_purchases = min_co_purchases

    def fit(self, lines: pd.DataFrame) -> "CategoryAffinityRecommender":
        lines = lines[lines["category"] != "unknown"]
        self.co_ = co_purchase_table(lines)
        self.popularity_ = lines["category"].value_counts().index.tolist()
        strong = self.co_[self.co_["co_purchases"] >= self.min_co_purchases]
        self.rules_ = strong.groupby("anchor")["recommended"].apply(list).to_dict()
        return self

    def recommend(self, category: str, k: int | None = None) -> list[str]:
        k = k or self.k
        recs = list(self.rules_.get(category, []))[:k]
        for c in self.popularity_:  # popularity fallback
            if len(recs) >= k:
                break
            if c != category and c not in recs:
                recs.append(c)
        return recs

    def popularity_baseline(self, category: str, k: int | None = None) -> list[str]:
        k = k or self.k
        return [c for c in self.popularity_ if c != category][:k]


def evaluation_cases(lines: pd.DataFrame) -> list[tuple[str, set[str]]]:
    """(anchor category, set of other categories actually bought) pairs."""
    cases = []
    for key in ("order_id", "customer_unique_id"):
        baskets = lines.groupby(key)["category"].apply(lambda s: set(s) - {"unknown"})
        for cats in baskets[baskets.str.len() > 1]:
            cases.extend((a, cats - {a}) for a in cats)
    return cases


def hit_rate(model: CategoryAffinityRecommender, cases, k: int, baseline: bool = False) -> float:
    fn = model.popularity_baseline if baseline else model.recommend
    hits = sum(bool(set(fn(a, k)) & rest) for a, rest in cases)
    return hits / len(cases)
