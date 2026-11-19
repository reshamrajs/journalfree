# JournalFree

[![Open the app](https://img.shields.io/badge/%E2%96%B6_Open_JournalFree-17803d?style=for-the-badge)](https://reshamrajs.github.io/journalfree/)
[![All tools](https://img.shields.io/badge/All_open_tools-555?style=for-the-badge)](https://reshamrajs.github.io/open-tools/)
[![Validate data](https://github.com/reshamrajs/journalfree/actions/workflows/validate.yml/badge.svg)](https://github.com/reshamrajs/journalfree/actions/workflows/validate.yml)

**Find high-impact journals you can publish in without paying an article processing charge (APC).**

Open-access fees of ₹1–3 lakh (US$1,500–4,000) per paper shut many researchers out of top journals,
especially students and early-career researchers in India and other low- and middle-income countries.
Most leading journals still have a **free subscription route**, and most let you share your accepted
manuscript openly (green open access). JournalFree lists them in one searchable place.

## Features

- Search by journal, publisher, subject or note
- Filter by subject, publisher, quartile and review speed; sort by impact factor, name or speed
- Impact factors that haven't been checked against JCR are flagged **unverified**
- Compare up to 3 journals side by side
- Filtered views live in the URL, so you can share a link to them
- No tracking, no cookies, no build step; works on phones; light and dark mode
- Weekly GitHub Action checks every journal link and opens an issue when one breaks

## Run it locally

```bash
python3 scripts/build_data.py        # validate data/journals.csv and write public/journals.json
python3 -m http.server -d public 8000
```

Open http://localhost:8000.

## Project layout

```
data/journals.csv        ← the single source of truth (edit this)
scripts/build_data.py    ← validates the CSV, writes public/journals.json
scripts/check_links.py   ← weekly link checker
public/                  ← the static site (index.html, app.js, style.css)
tests/                   ← unit tests for the validator
```

## Contributing

The easiest way to help is to **add a journal or fix a wrong value**. See [CONTRIBUTING.md](CONTRIBUTING.md).
No coding needed: open an issue with the "Suggest a journal or correction" form.

## Deploy

It's a static folder, so any static host works. On Cloudflare Pages or Netlify, set the build command
to `python3 scripts/build_data.py` and the output directory to `public`. On GitHub Pages, the included
`pages.yml` workflow publishes `public/` on every push to `main`.

## Disclaimer

Journal policies and impact factors change. Always confirm on the journal's own page before you submit.

## Licence

Code: [MIT](LICENSE). Data (`data/journals.csv`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
