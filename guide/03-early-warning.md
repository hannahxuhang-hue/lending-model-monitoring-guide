# 3. Early warning: signals before loan outcomes mature

Small-business and consumer installment loans typically take 12 months or more to show their default rate.
If you wait for defaults, a model problem that started today will not be visible until next year. This
chapter is about what you can measure **in the meantime**.

## 3.1 Decision rates (monthly)

Two numbers that every lender already has:

- **Approval rate.** Compare with the trailing six months. A change of 5 percentage points or more with no
  policy change behind it deserves an explanation.
- **Override rate.** The share of decisions where staff went against the model's recommendation. Rising
  overrides are one of the best signals that the model is missing something. Your lenders are compensating.
  Review a sample: are overrides concentrated in one product, one channel, one type of business?

Both are cheap, available immediately, and already understood by your board and credit committee.

## 3.2 Early delinquency against expectation (quarterly)

The central early-warning check: for loans that have been on the books long enough to show **early**
delinquency (for example 30+ days past due at 6 months on book), compare the actual count with what the model
implies.

What you need:

1. **Each loan's predicted probability of default (PD)** at booking. If your model produces a score rather
   than a PD, use the score-to-bad-rate table from development.
2. **The early-to-final ratio**: of the loans that eventually defaulted within 12 months in your development
   data (or history), what share were already 30+ days past due at 6 months? In the worked example it is
   about 41%.
3. **Expected early delinquencies** = sum of PD × early-to-final ratio.
4. **Actual early delinquencies**, from your servicing system.

Then:

```
ratio = actual / expected
p-value = probability of seeing "actual" or more if the model were right  (Poisson)
```

In a spreadsheet: `=1-POISSON(actual-1, expected, TRUE)`.

**Minimum count.** If fewer than 5 early delinquencies are expected, report *insufficient* rather than a ratio.
With so few expected, one or two loans would move the ratio by 20–40%. Wait for the next quarter to accumulate.

## 3.3 Vintage curves

Plot cumulative 30+ DPD rate by months on book, one line per booking quarter. A new vintage running above the
older ones at the same age is the same signal as 3.2, shown as a picture. Credit committees usually find this
chart easier to read than a ratio.

## 3.4 When an early warning fires

The model may not be the cause. Before changing anything:

1. **Segment the cohort.** Channel, product, industry, geography, loan size, booking month. Early delinquency is
   usually concentrated. In the worked example the red cohort also contains far more young businesses.
2. **Check what else changed at booking time.** Policy exceptions, a new partner, a promotional rate, a new
   underwriter, a local economic shock.
3. **Check whether stability alerts fired at the time.** If CSI flagged the same shift at booking, the two findings
   confirm each other.
4. **Report to credit committee** with the segment breakdown, not only the headline ratio.

A model change usually comes only after this analysis, and after performance ([chapter 4](04-performance-and-calibration.md))
confirms the problem once outcomes mature.
