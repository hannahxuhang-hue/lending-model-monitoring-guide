# 5. Fair-lending review: from outcomes to inputs

> This chapter describes analytical methods. It is not legal advice. The legal framework changed in 2026
> (see 5.5 and the [regulatory appendix](appendix-regulatory-context.md)). Decide what your institution is
> required to do with counsel.

Many lenders already run an **outcome** test: do approval rates or prices differ across demographic groups?
That test tells you *whether* there is a gap. It does not tell you *why*, and so it does not tell you what
to fix. This chapter adds the step that does: an **input-level review** asking which model inputs drive the
gap, whether each has a business justification, and whether an alternative would do the same job with less
disparity.

## 5.1 Estimating group membership when you do not collect it

Outside mortgage lending, most lenders do not collect applicants' race or ethnicity. The standard public
method for estimating it is **Bayesian Improved Surname Geocoding (BISG)**. It combines the
surname-by-race/ethnicity distribution from the Census with the demographic make-up of the applicant's
census tract or block group, and gives each applicant a *probability* of belonging to each group (Elliott et
al., 2009; CFPB, 2014). The CFPB has published its BISG code.

**Use the probabilities, not a single assigned group.** Assigning each applicant to their most likely group
misclassifies people systematically and biases the comparison. Instead, weight each applicant by their
probability: an applicant with a 0.7 probability counts as 0.7 of an applicant in the group and 0.3 in the
comparison group.

## 5.2 Outcome check (quarterly)

**Adverse impact ratio (AIR)** for approvals:

```
AIR = approval rate (group, probability-weighted) / approval rate (comparison group, probability-weighted)
```

Report it with a significance test (a two-proportion z-test on the weighted counts is a reasonable
approximation). A widely used screening heuristic flags AIR below 0.80. This guide suggests amber below 0.90
and red below 0.80. These are **screening triggers for further review, not legal standards**, and an amber
or red result is not a finding of discrimination.

For pricing, compare average rate or APR by group, controlling for the pricing factors your policy uses.

## 5.3 Input-level proxy review (annually, and whenever inputs change)

For **each input** in the model, measure two things:

1. **Association with estimated group membership.** For example, the rank correlation between the input and
   each applicant's group probability.
2. **Predictive value.** For example, the input's own AUC for default (folded so 0.5 = no signal), or the
   drop in model AUC when it is removed.

Then read them together:

| Association with group | Predictive value | Action |
|---|---|---|
| Low | Any | No further review needed for fair-lending purposes |
| High | High | Document the business justification: why this input measures creditworthiness, not group membership. Consider whether a more direct measure exists |
| **High** | **Low** | **First candidate for replacement or removal.** It is doing little credit work while tracking group membership |

Typical candidates in small-business and consumer lending: geographic variables (ZIP-level income, property
values), certain bank-account or device variables, education, and time at address. The point is not that
these are forbidden. It is that they need a stated reason.

`proxy_screen()` in [`monitoring_checks.py`](../examples/monitoring_checks.py) produces the table. In the
worked example, ZIP-level median income has a correlation of about −0.5 with group membership but almost no
predictive value of its own.

## 5.4 Less-discriminatory-alternative (LDA) search

For each flagged input (and, if feasible, a few others), refit the model **without** it (or with a
replacement) and compare the variants on **hold-out data**:

- predictive power (AUC);
- disparity (AIR) at the **same approval rate**. Otherwise a variant simply looks fairer because it approves more
  people.

Two practical points for small samples:

- **Repeat over many random splits** (the example uses 20) and report the average change and its spread. With
  a few hundred loans, one split can move AUC by a point on its own.
- **Compare the AUC change with the split-to-split noise.** A drop smaller than its own standard deviation is
  not a meaningful loss of predictive power.

In the worked example, removing ZIP-level income changes AUC by −0.004 (spread ±0.005) and improves AIR by
about 0.045. That is a candidate alternative with no meaningful loss of predictive power. Removing credit
score costs 0.056 of AUC and does not improve AIR.

For a more thorough treatment of LDA search, including searching across many alternative models, see Gillis,
Meursault & Ustun (2024) in the references.

## 5.5 Why do this when the legal standard has changed?

In April 2026 the CFPB amended Regulation B to state that ECOA does not recognise disparate-impact liability,
effective July 21, 2026. The input-level review remains useful for reasons that do not depend on that rule:

- **Proxy-based disparate treatment remains prohibited.** The same rule expressly preserves liability where a
  facially neutral input is used as a proxy for a protected characteristic. Identifying which inputs track group
  membership is how you find out whether you have one.
- **Other frameworks still apply.** The Fair Housing Act for mortgage and housing-related credit; state laws,
  several of which (including New York's) recognise effects-based claims; and CRA and prudential examination
  procedures.
- **Mission.** Many CDFIs, community development credit unions, and MDIs exist to serve the communities where
  these gaps appear. Knowing which inputs create a gap, and whether a better alternative exists, is part of
  doing that work well, whatever the enforcement climate.
- **Model quality.** An input with high group association and low predictive value is, first of all, a weak
  input.

## 5.6 Documentation

For each review, record: the method used to estimate group membership; the outcome results; the input table;
the LDA variants tested and their results; the decision taken for each flagged input and **why**. Use
[`templates/fair-lending-review-template.md`](../templates/fair-lending-review-template.md). A documented
decision to keep an input with a stated business reason is a sound outcome. An undocumented one is not.
