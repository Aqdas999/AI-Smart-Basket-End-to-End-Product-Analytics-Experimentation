"""Experiment design and analysis toolkit.

Everything an A/B test needs, implemented with numpy/scipy so each step is
visible: deterministic assignment, sample-size calculation, sample-ratio-
mismatch check, two-proportion z-test, delta-method test for ratio metrics
(randomised by customer, measured per order) and a cluster bootstrap.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Assignment
# ---------------------------------------------------------------------------
def assign_variant(unit_ids: pd.Series, salt: str = "smart-basket-v1", treatment_share: float = 0.5) -> pd.Series:
    """Deterministic hash-based assignment: the same customer always gets the
    same variant, on every order and every device, with no lookup table."""

    def bucket(uid: str) -> float:
        h = hashlib.md5(f"{salt}:{uid}".encode()).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    buckets = unit_ids.map(bucket)
    return pd.Series(np.where(buckets < treatment_share, "treatment", "control"), index=unit_ids.index)


# ---------------------------------------------------------------------------
# Design
# ---------------------------------------------------------------------------
def sample_size_two_proportions(p_baseline: float, mde_abs: float, alpha: float = 0.05, power: float = 0.80) -> int:
    """Units per arm to detect an absolute lift ``mde_abs`` (two-sided test)."""
    p1, p2 = p_baseline, p_baseline + mde_abs
    p_bar = (p1 + p2) / 2
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    n = (z_a * np.sqrt(2 * p_bar * (1 - p_bar)) + z_b * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / mde_abs**2
    return int(np.ceil(n))


def mde_for_sample_size(p_baseline: float, n_per_arm: int, alpha: float = 0.05, power: float = 0.80) -> float:
    """Smallest absolute lift detectable with ``n_per_arm`` units per arm."""
    lo, hi = 1e-6, 1 - p_baseline - 1e-6
    for _ in range(100):
        mid = (lo + hi) / 2
        if sample_size_two_proportions(p_baseline, mid, alpha, power) > n_per_arm:
            lo = mid
        else:
            hi = mid
    return hi


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
def srm_test(n_control: int, n_treatment: int, expected_share: float = 0.5) -> float:
    """Chi-square p-value for sample-ratio mismatch. p < 0.001 => stop, investigate."""
    total = n_control + n_treatment
    expected = [total * (1 - expected_share), total * expected_share]
    return float(stats.chisquare([n_control, n_treatment], expected).pvalue)


@dataclass
class TestResult:
    metric: str
    control: float
    treatment: float
    abs_diff: float
    rel_lift: float
    ci_low: float
    ci_high: float
    p_value: float

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def two_proportion_ztest(x_c: int, n_c: int, x_t: int, n_t: int, metric: str = "rate", alpha: float = 0.05) -> TestResult:
    p_c, p_t = x_c / n_c, x_t / n_t
    p_pool = (x_c + x_t) / (n_c + n_t)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_c + 1 / n_t))
    z = (p_t - p_c) / se_pool
    se = np.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
    zc = stats.norm.ppf(1 - alpha / 2)
    d = p_t - p_c
    return TestResult(metric, p_c, p_t, d, d / p_c, d - zc * se, d + zc * se, float(2 * stats.norm.sf(abs(z))))


def _ratio_mean_var(num: np.ndarray, den: np.ndarray) -> tuple[float, float]:
    """Delta-method mean and variance of sum(num)/sum(den) over i.i.d. units."""
    n = len(num)
    mx, my = num.mean(), den.mean()
    vx, vy = num.var(ddof=1), den.var(ddof=1)
    cxy = np.cov(num, den, ddof=1)[0, 1]
    r = mx / my
    var = (vx - 2 * r * cxy + r**2 * vy) / (my**2 * n)
    return r, var


def delta_method_ratio_test(
    df: pd.DataFrame, num: str, den: str, group_col: str = "variant", metric: str | None = None, alpha: float = 0.05
) -> TestResult:
    """Test a ratio metric (e.g. multi-product orders / orders) when the
    randomisation unit (customer) differs from the analysis unit (order).

    ``df`` must have one row per randomisation unit with summed ``num`` and
    ``den`` columns. Treating orders as independent would understate the
    variance — the mistake in the original version of this project.
    """
    c = df[df[group_col] == "control"]
    t = df[df[group_col] == "treatment"]
    r_c, v_c = _ratio_mean_var(c[num].to_numpy(float), c[den].to_numpy(float))
    r_t, v_t = _ratio_mean_var(t[num].to_numpy(float), t[den].to_numpy(float))
    d, se = r_t - r_c, np.sqrt(v_c + v_t)
    zc = stats.norm.ppf(1 - alpha / 2)
    p = float(2 * stats.norm.sf(abs(d / se)))
    return TestResult(metric or f"{num}/{den}", r_c, r_t, d, d / r_c, d - zc * se, d + zc * se, p)


def cluster_bootstrap_ratio(
    df: pd.DataFrame, num: str, den: str, group_col: str = "variant", n_boot: int = 2000, seed: int = 0
) -> tuple[float, float]:
    """95% bootstrap CI for the absolute difference of a ratio metric,
    resampling whole customers (clusters). Used to sanity-check the delta method."""
    rng = np.random.default_rng(seed)
    out = []
    groups = {g: d[[num, den]].to_numpy(float) for g, d in df.groupby(group_col)}
    for _ in range(n_boot):
        r = {}
        for g, arr in groups.items():
            s = arr[rng.integers(0, len(arr), len(arr))]
            r[g] = s[:, 0].sum() / s[:, 1].sum()
        out.append(r["treatment"] - r["control"])
    return tuple(np.percentile(out, [2.5, 97.5]))


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm–Bonferroni adjusted p-values (for secondary/segment metrics)."""
    p = np.asarray(p_values, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (len(p) - rank) * p[idx])
        adj[idx] = min(running, 1.0)
    return adj.tolist()
