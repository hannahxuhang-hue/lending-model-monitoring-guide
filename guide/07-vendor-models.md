# 7. Vendor models: monitoring what you cannot see inside

Most small lenders rely on at least one model they did not build: a bureau score, a cash-flow or
bank-data score, a fraud score, or a scorecard inside the loan-origination system. The model is the vendor's,
but the lending decision, and responsibility for it, remain yours.

## 7.1 What you can monitor without seeing the model

Almost everything in chapters 2–5, because those checks only need what passes through your hands:

| You have | So you can run |
|---|---|
| The inputs you send the vendor | Data quality, CSI |
| The score that comes back | Score PSI, approval and override rates |
| Your decisions and the loan outcomes | Early warning, AUC, calibration against your own book |
| Applicant name and address | BISG estimates → fair-lending outcome check |

What you usually **cannot** do is the input-level review (chapter 5.3) on inputs the vendor adds itself. That
is what 7.2 is for.

## 7.2 What to ask the vendor for

At contract, and at renewal:

1. **A description of the model**: what it predicts, over what window, on what population it was built.
2. **The inputs it uses**, at least by category, and which of them the vendor sources itself.
3. **Validation results**: rank-order and calibration performance, preferably on a population similar to
   yours (small-business, thin-file, a CDFI market), not only the vendor's overall book.
4. **The vendor's own fair-lending testing**: what it tests, how often, and a summary of results.
5. **Change notification**: advance notice of any change to inputs, methodology, or version, with release
   notes.
6. **Support for your monitoring**: score distributions by month, or the ability to export scores with
   application IDs.

If a vendor cannot provide items 1, 3, or 5, note that in your model inventory as a known limitation.

## 7.3 Your own performance evidence

Vendor validation describes the vendor's population. Your applicants may differ: smaller businesses,
thinner files, particular industries or neighbourhoods. Once you have 12 months of outcomes, compute AUC and
calibration **on your own book** (chapter 4). If the vendor score ranks your applicants much less well than
the vendor's documentation says, you have learned something important about fitness for your market.

## 7.4 When the vendor changes something

Treat a vendor version change like a new model:

- re-run score PSI and CSI on the first month of new-version scores against the last month of the old;
- if your cut-offs were set on the old version, check whether the approval rate moved;
- restart the baseline for early-warning and performance checks from the change date, and say so in the
  documentation.
