# 8. Documentation: what to write down

The purpose of documentation is that someone else (a new staff member, an auditor, an examiner, a funder, or
your future self) can see **what was checked, what was found, and what was decided, and why**. It does not
need to be long.

## 8.1 The four documents

| Document | Updated | Template |
|---|---|---|
| **Model inventory**: every model, owner, tier, inputs, last review | When anything changes | [`templates/model-inventory.csv`](../templates/model-inventory.csv) |
| **Monitoring policy**: cadence, thresholds, owners, escalation (in effect, chapter 6 adapted to your institution) | Annually | Chapter 6 + [`thresholds.csv`](../thresholds.csv) |
| **Monitoring report**: one per cycle, per model | Monthly or quarterly | [`templates/monitoring-report-template.md`](../templates/monitoring-report-template.md) |
| **Fair-lending review**: outcome results, input review, LDA search, decisions | Annually or on change | [`templates/fair-lending-review-template.md`](../templates/fair-lending-review-template.md) |

## 8.2 What a good monitoring report contains

1. **A status table at the top**: one row per check, with result, green/amber/red, and owner. Most readers
   stop here, so it must stand alone.
2. **Every amber and red item**: what was found on investigation and what was decided.
3. **Anything that changed** since the last report: data sources, vendor versions, products, policy, channels.
4. **Open items** carried from previous reports, with status.
5. **Sign-off**: who prepared it, who reviewed it, date.

## 8.3 Common gaps auditors and examiners find

- Monitoring was run but no one recorded what was done about an alert.
- Thresholds exist, but no one can say where they came from.
- The baseline was silently reset after a vendor change, so a shift disappeared.
- A model's use grew (from marketing to eligibility), but its tier and monitoring did not.
- Fair-lending outcome tests were run, but no one looked at which inputs drove a gap.

Each of these is a **documentation** gap, not an analytical one, and each is cheap to close.
