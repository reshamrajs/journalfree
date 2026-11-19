# Contributing to JournalFree

Thank you! Every journal you add saves someone a publication fee.

## Rules for listing a journal

A journal belongs here only if **all** of these are true:

1. You can publish in it **without paying** (a subscription or hybrid route with no mandatory APC).
2. It is ranked **Q1 or Q2** in JCR or Scopus.
3. You can link to an official page that confirms this.

## Option 1: no code (open an issue)

Use the **Suggest a journal or correction** issue form. A maintainer will add it.

## Option 2: pull request

1. Edit `data/journals.csv`. One row per journal. Columns:

   | column | example | notes |
   |---|---|---|
   | id | 18 | next unused whole number |
   | journal | Medical Image Analysis | official name |
   | publisher | Elsevier | |
   | subjects | Medical imaging;AI/ML | separate with `;` |
   | access_model | Subscription (hybrid) | |
   | indexing | SCIE | |
   | quartile | Q1 | `Q1`, `Q1/Q2` or `Q2` |
   | impact_factor | 6.3 | number only, or empty |
   | if_verified | yes | `yes` only if you checked JCR this year |
   | speed | Fast | `Fast`, `Moderate`, `Slow` or empty |
   | green_oa | Yes - AAM after embargo | from Sherpa Romeo or the journal |
   | url | https://... | must be https |
   | notes | Fast; broad scope | short |

2. Run the checks:

   ```bash
   python3 scripts/build_data.py
   python3 -m unittest discover -s tests
   ```

3. Commit both `data/journals.csv` and the regenerated `public/journals.json`, then open a PR and link your evidence.

## Code changes

The site is plain HTML, CSS and JavaScript in `public/`. Keep it framework-free and dependency-free.
Look for issues labelled **good first issue**.
