---
name: decks
description: >
  Validate and edit Recall flashcard decks and the three static pages that
  serve them. Checks decks against card.schema.json, keeps gospel.json and
  gospel_zh.json index-aligned, and keeps the shared nav and common.css
  cache-buster in sync across index.html, questions.html, and flashcards.html.
  Use when editing decks, cards, decks/manifest.json, docs/questions.md, site
  navigation, or stylesheet cache-busters, and when the user runs /decks.
---

# Decks

Recall is static files. The browser loads decks and the question guide with `fetch`, so work from a local HTTP server rooted at the repo. Opening the HTML files directly fails those requests.

```bash
python3 -m http.server 8000
```

Then use `http://localhost:8000/`.

## Deck edits

`card.schema.json` is the deck contract. `decks/manifest.json` is the picker list: each entry needs a unique `id`, the label shown on the picker (`name`), and a `file` that exists. `app.js` stamps `deck.name` from the deck file onto each card, falling back to the manifest label.

`decks/gospel.json` and `decks/gospel_zh.json` are one translation. Cards stay index-aligned: same count, same `type` at each index, and for `mc` cards the same option count and the same `answer` index. `decks/gospel_old.json` is not in the manifest and is not part of that pair. Leave it out of the picker unless the user asks to publish it.

Before finishing a deck or manifest change, run:

```bash
uv run --with jsonschema python .grok/skills/decks/scripts/check_decks.py
```

The script validates every `decks/*.json` except the manifest against `card.schema.json`, rejects an `mc` answer index past the last option, checks manifest paths, and checks the translation pair. Fix failures. Do not weaken the script to match a broken deck.

## Shared chrome

`header.site-nav` is copied in `index.html`, `questions.html`, and `flashcards.html`. The blocks match except `aria-current="page"`, which is set only on the link for that page. `index.html` has none.

`common.css?v=` is the same token on all three pages. After editing `common.css`, set one new token on every `common.css` link. After editing `style.css`, `questions.css`, or `flashcards.css`, bump only the link that points at that file.

`questions.html` fetches `docs/questions.md` and renders it. The other files in `docs/` are not loaded by the site.

## Check in the browser

Use the served origin, and reload so a cached deck is not what you are looking at.

- Deck or manifest change: `/flashcards.html`. The deck is listed. Start it, answer one multiple-choice card, and reveal one open-ended card.
- `docs/questions.md`: `/questions.html` shows the guide.
- Nav or `common.css`: `/`, `/questions.html`, and `/flashcards.html`.
- A page stylesheet: that page at a desktop width and a narrow viewport.
