# 6. Alerts, owners, and actions

Monitoring that produces numbers without decisions is a report nobody reads. This chapter turns each check
into a rule: **what level triggers an alert, who owns it, what they do first, and by when.**

## 6.1 Cadence

| Cadence | Checks |
|---|---|
| **Monthly** | Data quality · score PSI (pooled to quarterly if <150 applications/month) · approval and override rates |
| **Quarterly** | Input CSI · early-delinquency ratio for seasoning cohorts · fair-lending outcome check (AIR) |
| **Annually** (or when a cohort matures) | AUC and calibration · segment checks · input-level fair-lending review and LDA search · full review and decision |
| **On event** | Any change to inputs, data sources, vendor version, product, or policy → re-run stability on the next month's data |

The cadence runs on a calendar and does not wait for someone to ask. Before this, many small lenders reviewed a model
only after someone noticed a problem, and by then a lagging indicator such as default rates had usually been
wrong for months.

## 6.2 Starting thresholds

These are **starting points for a small portfolio**, set conservatively to avoid alert fatigue. Adopt them,
adjust them to your volume and risk appetite, and record the reasons in your monitoring policy. The same table
is in [`thresholds.csv`](../thresholds.csv) and in the spreadsheet calculator.

| Check | Amber | Red | Owner | First action |
|---|---|---|---|---|
| Data quality: missing rate per input | +5 pp vs baseline, or >2% outside baseline range | +10 pp, or field entirely blank | Data / loan-system admin | Find the cause; fix the feed before touching the model |
| Score PSI (5 bins) | ≥ max(0.10, noise threshold) | ≥ max(0.25, 2× noise threshold) | Model owner | Check which inputs moved; confirm whether the mix really changed |
| Input CSI (5 bins) | ≥ max(0.10, noise threshold) | ≥ max(0.25, 2× noise threshold) | Model owner | Were applicants like these in the development data? |
| Approval rate vs trailing 6 months | ±5 pp | ±10 pp | Chief lending officer | Explain (policy / mix / data); if unexplained, treat as a data alert |
| Override rate | >10% or doubled | >20% | Chief lending officer | Review a sample of overrides |
| Early delinquency, actual/expected | ≥1.25× | ≥1.50× and p < 0.05 | Chief lending officer | Segment the cohort; report to credit committee |
| AUC, matured cohort | Drop >0.03 and outside 95% interval | Drop >0.07 and outside interval | Model owner | Segment; if rank order degraded, plan rebuild |
| Calibration, actual/expected | Outside 0.80–1.25 | Outside 0.67–1.50 and interval excludes 1.0 | Model owner | Recalibrate if rank order holds; otherwise rebuild |
| Fair lending: approval AIR | <0.90 | <0.80 | Compliance lead / CLO | Run the input-level review; document |
| Fair lending: input association | \|corr\| ≥ 0.30 | ≥ 0.30 with weak predictive value | Compliance / model owner | Business justification; LDA test |
| Vendor change notice | Any change to inputs or method | Change without notice or documentation | Vendor relationship owner | Re-run stability; request documentation |

## 6.3 Owners

At a small lender one person may hold several of these roles. What matters is that **each alert has one
named person** who acknowledges it and records what happened. A typical assignment:

- **Model owner**: often the head of credit, risk, or analytics; the person who can explain what the model does.
- **Data owner**: whoever administers the loan-origination system or receives vendor files.
- **Chief lending officer**: decision rates, early warning, anything that affects lending policy.
- **Compliance lead**: fair-lending checks, with counsel as needed.
- **Board or credit committee**: receives every red alert and the annual review.

## 6.4 What happens when an alert fires

```
alert fires
   │
   ├─ acknowledge within 5 business days (owner records it)
   │
   ├─ INVESTIGATE: is it data, population, or model?
   │     data problem ─────────► fix the feed, re-run the check, close
   │     population change ────► expected? document; check the new segment at next review
   │     model problem ────────► go on
   │
   ├─ DECIDE:
   │     accept and monitor ───► document why; tighten cadence for that check
   │     recalibrate ──────────► rank order OK, level wrong
   │     rebuild / replace ────► rank order degraded, or input must be removed
   │     restrict use ─────────► e.g. manual review for the affected segment until fixed
   │
   └─ RECORD: what fired, what was found, what was decided, who decided, date
```

Every **red** alert goes to the credit committee or board with the investigation result, even if the answer
turned out to be "data problem, fixed."

## 6.5 Avoiding alert fatigue

- Use the sample-size-aware thresholds ([chapter 2](02-input-and-score-stability.md)); they remove most false alarms.
- Pool small periods rather than lowering standards.
- Review the thresholds once a year. If a check has never fired and never would have caught a known
  problem, it may be set too loose. If it fires every cycle and nothing is ever found, it is too tight.
