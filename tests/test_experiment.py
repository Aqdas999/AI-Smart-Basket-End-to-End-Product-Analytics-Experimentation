import numpy as np
import pandas as pd
import pytest
from scipy import stats

from smart_basket import experiment as ex
from smart_basket.recommender import CategoryAffinityRecommender, evaluation_cases, hit_rate


def test_assignment_is_deterministic_and_balanced():
    ids = pd.Series([f"cust-{i}" for i in range(20000)])
    a, b = ex.assign_variant(ids), ex.assign_variant(ids)
    assert (a == b).all()
    share = (a == "treatment").mean()
    assert 0.49 < share < 0.51
    other_salt = ex.assign_variant(ids, salt="another-test")
    assert 0.45 < (a == other_salt).mean() < 0.55  # independent across experiments


def test_sample_size_matches_textbook_value():
    # 10% -> 12% at alpha .05, power .8 needs ~3,841 per arm
    assert ex.sample_size_two_proportions(0.10, 0.02) == pytest.approx(3841, abs=5)


def test_mde_inverts_sample_size():
    n = ex.sample_size_two_proportions(0.03, 0.008)
    assert ex.mde_for_sample_size(0.03, n) == pytest.approx(0.008, abs=2e-4)


def test_srm_detects_imbalance():
    assert ex.srm_test(5000, 5050) > 0.1
    assert ex.srm_test(5000, 5600) < 0.001


def test_delta_method_equals_ztest_with_one_order_per_customer():
    rng = np.random.default_rng(0)
    n = 20000
    df = pd.DataFrame({"variant": np.where(rng.random(n) < 0.5, "control", "treatment"), "orders": 1})
    df["multi"] = (rng.random(n) < np.where(df["variant"] == "treatment", 0.05, 0.03)).astype(int)
    d = ex.delta_method_ratio_test(df, "multi", "orders")
    c, t = df[df.variant == "control"], df[df.variant == "treatment"]
    z = ex.two_proportion_ztest(c.multi.sum(), len(c), t.multi.sum(), len(t))
    assert d.abs_diff == pytest.approx(z.abs_diff)
    assert d.ci_low == pytest.approx(z.ci_low, rel=1e-3)


def test_delta_method_widens_ci_for_clustered_data():
    """Customers with many correlated orders must give a wider CI than an order-level test."""
    rng = np.random.default_rng(1)
    rows = []
    for i in range(3000):
        k = rng.integers(1, 8)
        p = rng.beta(1, 20)  # customer-specific propensity -> orders are correlated
        rows.append({"variant": "treatment" if i % 2 else "control", "orders": k, "multi": rng.binomial(k, p)})
    df = pd.DataFrame(rows)
    d = ex.delta_method_ratio_test(df, "multi", "orders")
    g = df.groupby("variant")[["multi", "orders"]].sum()
    naive = ex.two_proportion_ztest(g.loc["control", "multi"], g.loc["control", "orders"],
                                    g.loc["treatment", "multi"], g.loc["treatment", "orders"])
    assert (d.ci_high - d.ci_low) > (naive.ci_high - naive.ci_low)


def test_aa_false_positive_rate_is_nominal():
    rng = np.random.default_rng(2)
    df = pd.DataFrame({"orders": 1, "multi": (rng.random(4000) < 0.03).astype(int)})
    ps = []
    for i in range(300):
        df["variant"] = np.where(rng.random(len(df)) < 0.5, "control", "treatment")
        ps.append(ex.delta_method_ratio_test(df, "multi", "orders").p_value)
    assert 0.02 < np.mean(np.array(ps) < 0.05) < 0.09


def test_holm_adjustment():
    assert ex.holm_adjust([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])


def test_recommender_learns_affinity_and_beats_popularity():
    lines = pd.DataFrame(
        {
            "order_id": ["a", "a", "b", "b", "c", "d", "e", "f", "g"],
            "customer_unique_id": ["1", "1", "2", "2", "3", "4", "5", "6", "7"],
            "category": ["bed", "decor", "bed", "decor", "toys", "toys", "toys", "toys", "toys"],
        }
    )
    m = CategoryAffinityRecommender(k=1).fit(lines)
    assert m.recommend("bed") == ["decor"]
    assert m.popularity_baseline("bed") == ["toys"]
    cases = evaluation_cases(lines)
    assert hit_rate(m, cases, 1) > hit_rate(m, cases, 1, baseline=True)
