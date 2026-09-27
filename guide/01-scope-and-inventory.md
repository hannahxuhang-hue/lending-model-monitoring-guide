# 1. Scope: which models, and how much monitoring each gets

## What counts as a model here

For this guide, a model is anything that turns applicant or loan data into a number or a decision that
someone relies on. For a small lender that usually includes:

- a **credit score or scorecard** used to approve, decline, or price loans (your own, or one built into your
  loan-origination system);
- a **vendor score** (a bureau score, a cash-flow score, a fraud score) used in the decision;
- a **rules engine** or decision matrix combining several inputs into approve / refer / decline;
- a **marketing or outreach model** that decides who gets contacted;
- a **loss or reserve estimate** used in financial reporting.

A spreadsheet with a formula that decides who gets a loan counts. So does a vendor product whose internals
you cannot see.

## Step 1: write the inventory

Before monitoring anything, list what you have. One row per model, using
[`templates/model-inventory.csv`](../templates/model-inventory.csv):

| Field | Why it matters |
|---|---|
| Name and purpose | What decision it drives |
| Owner | The one person who answers for it |
| Built by | In-house, vendor, consultant |
| Inputs | What data it uses, and where each input comes from |
| Output and how it is used | Score, PD, approve/decline; what cut-off |
| Volume | Applications or loans scored per month |
| Materiality tier | See below |
| Date last reviewed | And by whom |

Most small lenders find two to five models. Many find one they had forgotten about.

## Step 2: assign a materiality tier

Monitoring effort should follow how much could go wrong. A simple three-tier rule:

| Tier | Typical example | Monitoring |
|---|---|---|
| **High** | Drives approve/decline or pricing on most of the loan book | Full set: monthly data quality and score stability; quarterly input stability, early warning and fair-lending outcomes; annual performance, calibration and input review |
| **Medium** | Informs decisions but a person makes the final call; or affects a minority of volume | Monthly data quality; quarterly stability and early warning; annual performance and fair-lending review |
| **Low** | Marketing prioritisation, internal reporting | Annual check that it still works and whether its use has grown |

Revisit the tier whenever the model's use changes. A marketing model that starts deciding who is
*offered* credit has moved up a tier.

## Step 3: fix the baseline

Every check in this guide compares *now* against a **baseline**, normally the sample the model was built or
last validated on. Save, once:

- the baseline distribution of each input and of the score (bin edges and shares);
- the baseline approval rate and override rate;
- the baseline default rate and the share of eventual defaults that were already 30+ days past due at 6 months
  on book (used in [chapter 3](03-early-warning.md));
- the baseline discrimination (AUC) with its confidence interval.

For a vendor model where you never saw the development data, use your **first six to twelve months of use**
as the baseline, and say so in the documentation.

## What this guide does not cover

- Validating a new model before first use (conceptual soundness, development testing). This guide starts
  once a model is in production.
- Generative-AI tools. They need different controls, and the April 2026 interagency guidance also leaves them
  out of scope (see the [regulatory appendix](appendix-regulatory-context.md)).
- Legal conclusions. Fair-lending questions about your specific products belong with counsel.
