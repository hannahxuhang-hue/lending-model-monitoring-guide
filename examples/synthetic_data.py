"""
Synthetic small-business loan data for the worked example.

Everything here is simulated. No real applicant, lender, or model is
represented. The data are sized like a small community lender: roughly
50-70 applications a month, a development sample of about 1,200 booked
loans, and 12-month default outcomes.

The simulation deliberately includes three things the guide teaches you
to catch:
  1. An applicant-mix shift (a new referral channel brings younger businesses).
  2. A data-feed problem (one input starts arriving blank for part of the book).
  3. An input that tracks estimated group membership much more strongly than it
     predicts repayment (a proxy candidate for the fair-lending review).

`group_prob` stands in for a BISG-style estimated probability that an
applicant belongs to a group of interest. It is simulated, not computed from
names or addresses.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

INPUTS = ["credit_score", "years_in_business", "log_annual_revenue",
          "debt_service_coverage", "prior_delinquencies", "zip_median_income_k"]


def _applicants(n: int, rng: np.random.Generator, young_business_share: float = 0.25) -> pd.DataFrame:
    g = rng.binomial(1, 0.40, n)                                   # latent group (never observed)
    group_prob = np.where(g == 1, rng.beta(6, 2, n), rng.beta(2, 6, n))
    young = rng.binomial(1, young_business_share, n)
    df = pd.DataFrame({
        "credit_score": np.clip(rng.normal(690 - 12 * g, 45, n), 520, 820).round(),
        "years_in_business": np.where(young == 1, rng.gamma(1.5, 0.8, n), rng.gamma(3.0, 2.2, n)).round(1),
        "log_annual_revenue": rng.normal(12.4 - 0.1 * g, 0.8, n).round(3),
        "debt_service_coverage": np.clip(rng.normal(1.45, 0.35, n), 0.6, 3.5).round(2),
        "prior_delinquencies": rng.poisson(0.35 + 0.08 * g, n),
        "zip_median_income_k": np.clip(rng.normal(78 - 24 * g, 14, n), 25, 180).round(1),
        "group_prob": group_prob.round(3),
    })
    return df


def _true_default_prob(df: pd.DataFrame) -> np.ndarray:
    z = (-2.0
         - 0.013 * (df["credit_score"] - 690)
         - 0.12 * (df["years_in_business"].clip(upper=15) - 5)
         - 0.9 * (df["debt_service_coverage"] - 1.45)
         + 0.40 * df["prior_delinquencies"]
         - 0.25 * (df["log_annual_revenue"] - 12.4)
         - 0.016 * (df["zip_median_income_k"] - 70))                # weak true effect
    return 1 / (1 + np.exp(-z))


def _outcomes(df: pd.DataFrame, rng: np.random.Generator, stress: float = 1.0,
              early_share: float = 0.45) -> pd.DataFrame:
    p = np.clip(_true_default_prob(df) * stress, 0, 0.95)
    df = df.copy()
    df["default_12m"] = rng.binomial(1, p)
    df["dpd30_at_6mob"] = (df["default_12m"] == 1) & (rng.random(len(df)) < early_share)
    df["dpd30_at_6mob"] = df["dpd30_at_6mob"].astype(int)
    return df


def generate(seed: int = 7) -> dict[str, pd.DataFrame]:
    """Return development, monitoring-quarter, and seasoned-cohort samples."""
    rng = np.random.default_rng(seed)

    development = _outcomes(_applicants(1200, rng), rng)

    # Q1: business as usual (about 60 applications a month).
    q1 = _applicants(180, rng)

    # Q2: a new referral partner sends more young businesses, and the
    # debt-service-coverage field arrives blank for ~15% of files after a
    # loan-origination-system update.
    q2 = _applicants(190, rng, young_business_share=0.55)
    broken = rng.random(len(q2)) < 0.15
    q2.loc[broken, "debt_service_coverage"] = np.nan

    # A cohort booked a year ago, now 12 months on book (outcomes known), and a
    # cohort booked 6 months ago (only early delinquency is known). The later
    # cohort is modestly stressed to mimic a local downturn.
    matured = _outcomes(_applicants(420, rng), rng, stress=1.0)
    seasoning = _outcomes(_applicants(360, rng, young_business_share=0.45), rng, stress=1.35)
    seasoning = seasoning.drop(columns=["default_12m"])             # not observed yet

    return {"development": development, "q1": q1, "q2": q2,
            "matured_cohort": matured, "seasoning_cohort": seasoning}
