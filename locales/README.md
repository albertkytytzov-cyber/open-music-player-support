# Support and privacy translations

The six JSON files contain full translations of the published English
`support.html` and `privacy.html` text, using the source state from 23 September
2026. Policy content remains dated 16 September 2026; the translations carry
their own 24 September date. This update does not introduce new data collection,
consent terms or retention periods.

Each privacy translation preserves all ten English sections and 24 paragraphs.
Support button names were checked against the app's nine-language UI dictionary.
The Russian policy predates this work and includes more detailed explanations;
its existing text is preserved. English and Russian pages remain authored HTML.

To edit a new translation, update the corresponding JSON, then run:

```sh
python3 scripts/build-localized-pages.py
node scripts/check-site.mjs
```

Commit both JSON and generated HTML. The output is ordinary static HTML: no
translation API, language-detection script, cookie or new network service.
All sixteen support/privacy pages include reciprocal language links, canonical
URLs and `hreflang` alternates; each localized news article links to its own
language's support/privacy pages. The sitemap includes every new page.

Browser checks on 24 September covered all six new language pairs at widths
320 and 390 px, plus direct desktop navigation. Long headings, date badges,
language links and Japanese line breaks were adjusted after visual inspection.
The temporary preview gallery is excluded from source and production packages.
