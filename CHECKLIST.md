# Model monitoring checklist (one page)

For each model in your inventory. Tick, record the result in the monitoring report, and escalate any red.

## Once (and when anything changes)
- [ ] Model is in the inventory with a named owner and a materiality tier
- [ ] Baseline saved: input and score bin edges and shares, approval and override rates, default rate, early-to-final ratio, AUC with interval
- [ ] Thresholds adopted (start from [`thresholds.csv`](thresholds.csv)) and the reasons recorded
- [ ] For vendor models: documentation requested (description, inputs, validation, fair-lending testing, change notice)

## Monthly
- [ ] **Data quality:** missing rate and out-of-range share for every input vs baseline
- [ ] **Score PSI** (5 bins, compared against the noise threshold; pool to quarterly if <150 applications/month)
- [ ] **Approval rate** vs trailing 6 months
- [ ] **Override rate** and a short look at why overrides happened

## Quarterly
- [ ] **Input CSI** for every input
- [ ] **Early warning:** actual vs expected 30+ DPD at 6 months on book, for each cohort that has reached 6 months (report "insufficient" if <5 expected)
- [ ] **Vintage curve** updated
- [ ] **Fair-lending outcome check:** probability-weighted approval AIR (and pricing, if risk-based)

## Annually (or when a cohort matures)
- [ ] **AUC and KS** with 95% interval, overall and by key segment
- [ ] **Calibration:** actual vs expected, overall and by PD band, with intervals
- [ ] **Input-level fair-lending review:** association with group membership × predictive value, per input
- [ ] **LDA search** for flagged inputs (repeated hold-out splits, same approval rate)
- [ ] **Decision recorded:** continue / recalibrate / rebuild / restrict / retire, and why
- [ ] **Thresholds reviewed:** too many false alarms? any known problem missed?
- [ ] Annual review presented to credit committee or board

## On every event
- [ ] New data source, form, system release, vendor version, product, channel, or policy → re-run data quality and stability on the next month
- [ ] Every alert: acknowledged within 5 business days, investigated (data / population / model), decided, recorded
