# 2. Data quality and stability: is the model still seeing what it was built for?

Loan outcomes take months to arrive. Inputs and scores are available the day an application comes in. The
checks in this chapter are therefore the first line of monitoring: they tell you the model is being fed
something different **before** that difference shows up as losses.

## 2.1 Data quality (monthly)

The cheapest check, and in practice the one that catches the most problems. For each input, compare with
baseline:

- **Missing rate.** A field that used to be 0% blank and is now 15% blank usually means a system change, a new
  application form, or a vendor feed failure.
- **Out-of-range share.** Values outside the baseline's 0.1st–99.9th percentile (negative revenue, a credit
  score of 999, a coverage ratio of 50).
- **Default-value spikes.** A sudden cluster at 0, at a round number, or at whatever value your system
  writes when a field is empty.

Why it matters: most models fill in something when an input is blank, usually the median. Weaker applicants
with a blank field then look average, and approvals rise for no good reason. The [worked example](../examples/walkthrough.ipynb)
shows exactly this: a feed problem on one field raised the approval rate by about 5 percentage points.

**Rule: fix a data alert before drawing any conclusion about the model.**

## 2.2 Population Stability Index (PSI) and Characteristic Stability Index (CSI)

PSI measures how far the current distribution of a variable has moved from baseline:

```
PSI = Σ over bins  (current share − baseline share) × ln(current share / baseline share)
```

Applied to the score it is called PSI; applied to an input it is often called CSI. Same formula.

How to compute it:

1. Split the **baseline** into bins with equal counts (quantiles). **Fix those bin edges and never recompute
   them** from current data.
2. Count current applications in each bin. Add a separate bin for missing values.
3. Apply the formula. If a bin is empty, use a small floor (0.01%) so the logarithm is defined.

## 2.3 The small-sample problem with PSI

The widely quoted thresholds (below 0.10 stable, 0.10–0.25 moderate shift, above 0.25 significant shift)
come from large-portfolio practice. **They ignore sample size.** PSI is never exactly zero, even when nothing
has changed, because any finite sample is noisy. The smaller the sample, the larger PSI is from noise alone.

A simulation in the worked example (2,000 draws with *no* real shift, against a 1,200-loan baseline):

| Applications in the period | Bins | Median PSI from noise alone | 99th percentile |
|---|---|---|---|
| 60 (one month at a small lender) | 10 | 0.155 | 0.817 |
| 60 | 5 | 0.061 | 0.250 |
| 180 (one quarter) | 5 | 0.022 | 0.086 |
| 1,200 | 5 | 0.006 | 0.020 |

With one month of applications and ten bins, a lender following the rule of thumb would be "investigating a
moderate shift" most months when nothing has happened. People soon learn to ignore the alerts, and then
they miss the real one.

**What to do:**

- **Use 5 bins, not 10**, when you score fewer than a few hundred applications per period.
- **Pool to quarterly** if you have fewer than about 150 applications a month.
- **Alert at the larger of the rule of thumb and a noise threshold.** When nothing has changed, PSI × n_eff
  approximately follows a chi-square distribution with (bins − 1) degrees of freedom, where
  n_eff = n_baseline × n_current / (n_baseline + n_current) (see Yurdakul, 2018, in the references). So the
  99% noise threshold is

  ```
  noise threshold = CHIINV(0.01, bins − 1) / n_eff
  ```

  In a spreadsheet, [`monitoring-calculator.xlsx`](../spreadsheet/monitoring-calculator.xlsx) does this for
  you. In Python, `psi_noise_threshold()` in [`monitoring_checks.py`](../examples/monitoring_checks.py).
  The approximation understates noise when bins hold fewer than about 10 applications, which is another reason
  to use fewer bins.

## 2.4 Reading stability results

| Pattern | Likely meaning | Next step |
|---|---|---|
| One input moves, score stable | Either the shift is small relative to the model's use of that input, or other inputs are offsetting it | Check whether the model was built on applicants like the new ones. If the new values sit outside the development range, the model is extrapolating even if the score looks calm |
| Score moves, inputs stable individually | Several small input shifts adding up, or a change in how inputs combine (e.g. a new product mix) | Look at CSI for all inputs together, and at the mix by channel/product |
| Score and one input move together | A genuine change in who is applying, or a data problem in that input | Check data quality for that input first; then look for a new channel, product, or market event |
| Everything moves at once | A system change, a new application form, or a new vendor version | Treat as a data incident until proven otherwise |

A population shift is not automatically a problem. If you opened a new referral channel on purpose, a shift
is expected. The monitoring record should say so, and the next performance review should check the new
segment separately.
