# 4. Performance and calibration: once outcomes are known

When a cohort of loans reaches the outcome window (for example 12 months on book), two questions can finally
be answered:

1. **Does the model still rank risk correctly?** Do defaulters score worse than non-defaulters? This is
   *discrimination*, measured by AUC (also called the c-statistic; Gini = 2 × AUC − 1) and KS.
2. **Are the predicted default rates at the right level?** This is *calibration*: expected vs actual defaults.

These are different failures with different fixes.

## 4.1 Rank order: AUC and KS, always with an interval

AUC is the probability that a randomly chosen defaulter scores worse than a randomly chosen non-defaulter.
0.5 is a coin flip; small-business scorecards often sit between 0.65 and 0.80.

**The small-lender issue:** the uncertainty in AUC depends mainly on the number of **defaults**, not the number
of loans. With 60 defaults, a 95% interval is typically ±0.07. A drop from 0.72 to 0.69 is well inside that
and is not evidence of anything.

Always report AUC with its interval. The Hanley–McNeil formula (Hanley & McNeil, 1982) needs only AUC and the
two counts. `auc_with_ci()` in [`monitoring_checks.py`](../examples/monitoring_checks.py) implements it.

**Starting rule** (see [chapter 6](06-alerts-owners-actions.md)):

- **Amber:** AUC drop > 0.03 **and** development AUC lies outside the cohort's 95% interval.
- **Red:** AUC drop > 0.07 **and** outside the interval.

If you have too few defaults for the interval to be informative (fewer than about 30), **pool two cohorts**
rather than reporting a number nobody should rely on.

## 4.2 Calibration: expected vs actual

Split the matured cohort into 5 bands by predicted PD. For each band, compare the sum of predicted PDs
(expected defaults) with actual defaults. Also compute the ratio for the whole cohort.

Give each ratio a confidence interval (an exact Poisson interval on the actual count; `calibration_table()`
does it). A band with 5 expected defaults and 2 actual has a ratio of 0.4 and an interval from roughly 0.05
to 1.4. On its own, that tells you almost nothing.

**Reading it:**

| Pattern | Meaning | Fix |
|---|---|---|
| All bands too high or too low by a similar factor | Level has shifted (economy, pricing, product mix) but ranking holds | **Recalibrate**: adjust the intercept or the score-to-PD mapping. Cheap, low risk |
| Low bands fine, high bands off (or vice versa) | Slope is wrong: the model is over- or under-confident | Recalibrate slope and intercept |
| Ratio fine but AUC has dropped | The model can no longer separate good from bad | **Rebuild** or re-select inputs |
| One segment off, the rest fine | A segment the model does not handle (new channel, industry) | Segment rule, overlay, or targeted rebuild |

## 4.3 Segment checks

Repeat AUC and calibration for the segments that matter to your mission and your book: product, channel,
loan size, new vs existing business, geography. Small segments will have wide intervals. The point is to
spot a segment that is clearly different, not to produce precise numbers for each.

## 4.4 The annual review

Once a year, or when a large cohort matures, bring the pieces together in a single review:

- stability over the year (chapter 2);
- early-warning results and whether they were borne out;
- performance and calibration, overall and by segment;
- the fair-lending review ([chapter 5](05-fair-lending-review.md));
- a decision: **continue**, **recalibrate**, **rebuild**, or **retire**, with the reasoning.

Use [`templates/monitoring-report-template.md`](../templates/monitoring-report-template.md).
