"""
Monitoring checks for lending models at small institutions.

Plain functions over pandas/numpy. No framework, no service, no database.
Each function maps to a section of the guide (see ../guide/).

All thresholds used here are the illustrative starting points from
guide/06-alerts-owners-actions.md. Calibrate them to your own portfolio.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# 1. Stability: PSI / CSI  (guide/02-input-and-score-stability.md)
# ---------------------------------------------------------------------------

def make_bins(baseline: pd.Series, n_bins: int = 5) -> np.ndarray:
    """Quantile bin edges from the baseline (development) sample.

    Edges are fixed once and reused every period, so that each period is
    compared against the same buckets. Outer edges are open (-inf, +inf).
    """
    qs = np.linspace(0, 1, n_bins + 1)[1:-1]
    inner = np.unique(np.quantile(baseline.dropna(), qs))
    return np.concatenate(([-np.inf], inner, [np.inf]))


def bin_shares(values: pd.Series, edges: np.ndarray, include_missing: bool = True) -> pd.Series:
    """Share of observations in each bin (plus a 'missing' bucket if requested)."""
    cats = pd.cut(values, bins=edges, include_lowest=True)
    shares = cats.value_counts(sort=False, normalize=False).astype(float)
    shares.index = shares.index.astype(str)
    if include_missing:
        shares["missing"] = float(values.isna().sum())
    return shares / len(values)


def psi(expected_shares: pd.Series, actual_shares: pd.Series, floor: float = 1e-4) -> float:
    """Population Stability Index between two sets of bin shares.

    PSI = sum over bins of (actual - expected) * ln(actual / expected).
    A small floor prevents division by zero when a bin is empty.
    """
    e = np.clip(expected_shares.values, floor, None)
    a = np.clip(actual_shares.reindex(expected_shares.index).fillna(0).values, floor, None)
    return float(np.sum((a - e) * np.log(a / e)))


def psi_noise_threshold(n_baseline: int, n_current: int, n_bins: int, alpha: float = 0.01) -> float:
    """PSI value that pure sampling noise would exceed only `alpha` of the time.

    With no real shift, PSI * n_eff is approximately chi-square with
    (n_bins - 1) degrees of freedom, where n_eff = n1*n2/(n1+n2).
    At small sample sizes this noise floor can be larger than the usual
    0.10 / 0.25 rules of thumb, which is why a small lender should compare
    against max(rule_of_thumb, noise_threshold) rather than the rule alone.
    """
    n_eff = n_baseline * n_current / (n_baseline + n_current)
    return float(stats.chi2.ppf(1 - alpha, n_bins - 1) / n_eff)


def stability_report(baseline: pd.DataFrame, current: pd.DataFrame, columns: list[str],
                     n_bins: int = 5, amber: float = 0.10, red: float = 0.25) -> pd.DataFrame:
    """PSI for the score and CSI for each input, with sample-size-aware status."""
    rows = []
    for col in columns:
        edges = make_bins(baseline[col], n_bins)
        exp = bin_shares(baseline[col], edges)
        act = bin_shares(current[col], edges)
        value = psi(exp, act)
        noise = psi_noise_threshold(len(baseline), len(current), len(exp))
        amber_t, red_t = max(amber, noise), max(red, noise * 2)
        status = "red" if value >= red_t else "amber" if value >= amber_t else "green"
        rows.append({
            "variable": col,
            "psi": round(value, 4),
            "noise_threshold_99": round(noise, 4),
            "amber_at": round(amber_t, 4),
            "red_at": round(red_t, 4),
            "missing_rate_baseline": round(baseline[col].isna().mean(), 4),
            "missing_rate_current": round(current[col].isna().mean(), 4),
            "status": status,
        })
    return pd.DataFrame(rows)


def data_quality_report(baseline: pd.DataFrame, current: pd.DataFrame, columns: list[str],
                        amber_pp: float = 0.05, red_pp: float = 0.10) -> pd.DataFrame:
    """Missing-rate and range checks: the cheapest, most often useful monthly check."""
    rows = []
    for col in columns:
        b_miss, c_miss = baseline[col].isna().mean(), current[col].isna().mean()
        lo, hi = baseline[col].quantile([0.001, 0.999])
        out_of_range = ((current[col] < lo) | (current[col] > hi)).mean()
        delta = c_miss - b_miss
        status = "red" if delta >= red_pp else "amber" if delta >= amber_pp or out_of_range > 0.02 else "green"
        rows.append({"variable": col, "missing_baseline": round(b_miss, 4), "missing_current": round(c_miss, 4),
                     "share_outside_baseline_range": round(out_of_range, 4), "status": status})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Early warning before outcomes mature  (guide/03-early-warning.md)
# ---------------------------------------------------------------------------

def early_warning_ratio(df: pd.DataFrame, pd_col: str, early_flag_col: str,
                        early_to_final_ratio: float, min_expected: float = 5.0) -> dict:
    """Actual vs expected early-payment-default count for loans seasoned enough.

    expected early defaults = sum(PD) * early_to_final_ratio, where the ratio
    (e.g. share of 12-month defaults that are already 30+ DPD at 6 months on
    book) comes from your development data or history. If the expected count is
    below `min_expected`, the check reports 'insufficient' rather than a ratio
    that would swing wildly on one or two loans.
    """
    expected = df[pd_col].sum() * early_to_final_ratio
    actual = int(df[early_flag_col].sum())
    if expected < min_expected:
        return {"loans": len(df), "expected": round(expected, 1), "actual": actual,
                "ratio": None, "p_value": None, "status": "insufficient"}
    ratio = actual / expected
    p = float(stats.poisson.sf(actual - 1, expected))  # P(X >= actual)
    status = "red" if ratio >= 1.5 and p < 0.05 else "amber" if ratio >= 1.25 else "green"
    return {"loans": len(df), "expected": round(expected, 1), "actual": actual,
            "ratio": round(ratio, 2), "p_value": round(p, 4), "status": status}


def decision_rates(df: pd.DataFrame, approved_col: str = "approved", override_col: str = "override") -> dict:
    return {"applications": len(df),
            "approval_rate": round(df[approved_col].mean(), 4),
            "override_rate": round(df[override_col].mean(), 4)}


# ---------------------------------------------------------------------------
# 3. Performance once outcomes mature  (guide/04-performance.md)
# ---------------------------------------------------------------------------

def auc_with_ci(y: np.ndarray, score: np.ndarray, level: float = 0.95) -> dict:
    """AUC with a Hanley-McNeil confidence interval.

    With few defaults the interval is wide; a drop that stays inside it is
    not evidence the model got worse.
    """
    y, score = np.asarray(y), np.asarray(score)
    n1, n0 = int(y.sum()), int(len(y) - y.sum())
    ranks = stats.rankdata(score)
    auc = (ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    q1, q2 = auc / (2 - auc), 2 * auc ** 2 / (1 + auc)
    se = np.sqrt((auc * (1 - auc) + (n1 - 1) * (q1 - auc ** 2) + (n0 - 1) * (q2 - auc ** 2)) / (n1 * n0))
    z = stats.norm.ppf(0.5 + level / 2)
    return {"defaults": n1, "non_defaults": n0, "auc": round(auc, 4),
            "ci_low": round(auc - z * se, 4), "ci_high": round(auc + z * se, 4)}


def ks_statistic(y: np.ndarray, score: np.ndarray) -> float:
    y, score = np.asarray(y), np.asarray(score)
    return float(stats.ks_2samp(score[y == 1], score[y == 0]).statistic)


def calibration_table(df: pd.DataFrame, pd_col: str, outcome_col: str, n_bands: int = 5) -> pd.DataFrame:
    """Expected vs actual default counts by predicted-PD band, with a Poisson interval."""
    bands = pd.qcut(df[pd_col], q=n_bands, duplicates="drop", precision=3)
    g = df.groupby(bands, observed=True).agg(loans=(outcome_col, "size"),
                                             expected=(pd_col, "sum"),
                                             actual=(outcome_col, "sum"))
    g["actual_to_expected"] = (g["actual"] / g["expected"]).round(2)
    lo = stats.chi2.ppf(0.025, 2 * g["actual"]) / 2
    hi = stats.chi2.ppf(0.975, 2 * (g["actual"] + 1)) / 2
    g["ratio_ci_low"] = (np.nan_to_num(lo) / g["expected"]).round(2)
    g["ratio_ci_high"] = (hi / g["expected"]).round(2)
    g["expected"] = g["expected"].round(1)
    g.index = [f"{iv.left:.1%} - {iv.right:.1%}" for iv in g.index]
    g.index.name = "pd_band"
    return g.reset_index()


# ---------------------------------------------------------------------------
# 4. Fair-lending review  (guide/05-fair-lending-review.md)
# ---------------------------------------------------------------------------

def adverse_impact_ratio(df: pd.DataFrame, group_prob_col: str, approved_col: str = "approved") -> dict:
    """Approval-rate ratio using probability-weighted group membership.

    `group_prob_col` holds each applicant's estimated probability of belonging
    to the group of interest (e.g. from BISG). Weighting by probability, rather
    than assigning each applicant to their most likely group, is the approach
    used in the public BISG literature and avoids systematic misclassification.
    The comparison group is weighted by (1 - p).
    """
    p = df[group_prob_col].values
    a = df[approved_col].values
    n_g, n_c = p.sum(), (1 - p).sum()
    rate_g, rate_c = (p * a).sum() / n_g, ((1 - p) * a).sum() / n_c
    air = rate_g / rate_c
    # Two-proportion z-test on effective counts (approximate).
    pooled = (p * a + (1 - p) * a).sum() / (n_g + n_c)
    se = np.sqrt(pooled * (1 - pooled) * (1 / n_g + 1 / n_c))
    z = (rate_g - rate_c) / se
    pval = float(2 * stats.norm.sf(abs(z)))
    status = "red" if air < 0.80 else "amber" if air < 0.90 else "green"
    return {"effective_n_group": round(n_g, 1), "effective_n_comparison": round(n_c, 1),
            "approval_rate_group": round(rate_g, 4), "approval_rate_comparison": round(rate_c, 4),
            "air": round(air, 3), "p_value": round(pval, 4), "status": status}


def proxy_screen(df: pd.DataFrame, inputs: list[str], group_prob_col: str, outcome_col: str,
                 proxy_flag: float = 0.30) -> pd.DataFrame:
    """For each input: how strongly it tracks estimated group membership,
    and how much it tells you about repayment.

    An input that correlates strongly with group membership but adds little
    predictive value is the first candidate for a business-justification
    review and a less-discriminatory-alternative (LDA) test.
    """
    rows = []
    for col in inputs:
        x = df[col].fillna(df[col].median())
        corr_group = stats.spearmanr(x, df[group_prob_col]).statistic
        # Univariate AUC of the input for the outcome, folded so 0.5 = no signal.
        auc = auc_with_ci(df[outcome_col].values, x.values)["auc"]
        rows.append({"input": col,
                     "corr_with_group_prob": round(float(corr_group), 3),
                     "univariate_auc": round(max(auc, 1 - auc), 3),
                     "review": "yes" if abs(corr_group) >= proxy_flag else "no"})
    return pd.DataFrame(rows).sort_values("corr_with_group_prob", key=abs, ascending=False)


def lda_search(df: pd.DataFrame, inputs: list[str], candidates: list[str], outcome_col: str,
               group_prob_col: str, approve_share: float, n_splits: int = 20, seed: int = 0) -> pd.DataFrame:
    """Refit the model without each candidate input and compare predictive
    power (AUC) and approval-rate parity (AIR) on hold-out samples.

    Repeats over `n_splits` random 60/40 splits, because with a few hundred
    loans a single split can move AUC by a point or two on its own.
    `approve_share` fixes the share approved, so each variant is compared at
    the same approval volume — otherwise AIR differences just reflect a looser
    cut-off.
    """
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    variants = {"current model": inputs}
    variants.update({f"without {c}": [i for i in inputs if i != c] for c in candidates})
    records = []
    for k in range(n_splits):
        train, test = train_test_split(df, test_size=0.4, random_state=seed + k, stratify=df[outcome_col])
        for label, cols in variants.items():
            model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                  LogisticRegression(max_iter=1000))
            model.fit(train[cols], train[outcome_col])
            pd_hat = model.predict_proba(test[cols])[:, 1]
            tmp = test[[group_prob_col]].copy()
            tmp["approved"] = (pd_hat <= np.quantile(pd_hat, approve_share)).astype(int)
            records.append({"variant": label, "split": k,
                            "auc": auc_with_ci(test[outcome_col].values, pd_hat)["auc"],
                            "air": adverse_impact_ratio(tmp, group_prob_col)["air"]})
    r = pd.DataFrame(records)
    base = r[r.variant == "current model"].set_index("split")
    r["auc_change"] = r["auc"].values - base.loc[r["split"], "auc"].values
    r["air_change"] = r["air"].values - base.loc[r["split"], "air"].values
    out = r.groupby("variant", sort=False).agg(
        auc=("auc", "mean"), air=("air", "mean"),
        auc_change=("auc_change", "mean"), auc_change_sd=("auc_change", "std"),
        air_change=("air_change", "mean"), air_change_sd=("air_change", "std"))
    return out.round(4).reset_index()
