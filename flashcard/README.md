# Recall — Flashcards

A small, build-free flashcard app for reviewing **multiple-choice** and **open-ended** questions. It loads decks from JSON files and runs entirely as static files, so it hosts cleanly on **GitHub Pages**.

- **No build step.** Just HTML, CSS, and JavaScript — [Vue 3](https://vuejs.org/) and [Pico CSS](https://picocss.com/) are loaded from a CDN.
- **Multiple decks at once.** Select any combination of decks, optionally shuffle, and study them as one queue.
- **Two card types.** Multiple choice (click an option for instant feedback) and open-ended (think, then reveal the answer).

## Run it locally

The app fetches JSON at runtime, which browsers block on `file://`, so serve the folder over HTTP:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/>.

## Add your own deck

1. Create a JSON file in `decks/`, e.g. `decks/history.json`:

   ```json
   {
     "name": "World History",
     "cards": [
       {
         "type": "mc",
         "question": "In which year did World War II end?",
         "options": ["1943", "1945", "1948"],
         "answer": 1,
         "explanation": "Japan formally surrendered in September 1945."
       },
       {
         "type": "open",
         "question": "Who was the first President of the United States?",
         "answer": "George Washington, who served from 1789 to 1797."
       }
     ]
   }
   ```

2. Register it in `decks/manifest.json`:

   ```json
   {
     "decks": [
       { "id": "history", "name": "World History", "file": "./decks/history.json" }
     ]
   }
   ```

### Card schema

| Field         | Type       | Applies to | Description                                          |
| ------------- | ---------- | ---------- | ---------------------------------------------------- |
| `type`        | string     | both       | `"mc"` or `"open"`.                                  |
| `question`    | string     | both       | The prompt shown on the card.                        |
| `options`     | string[]   | `mc`       | Answer choices.                                      |
| `answer`      | number     | `mc`       | 0-based index of the correct option in `options`.    |
| `answer`      | string     | `open`     | The answer text revealed on demand.                  |
| `explanation` | string     | both       | Optional note shown after the card is answered.      |

## Deploy to GitHub Pages

1. Push this folder to a GitHub repository (files at the repo root).
2. In the repo, go to **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**, select your branch (e.g. `main`) and the `/ (root)` folder, then **Save**.
4. Your app will be live at `https://<your-username>.github.io/<repo-name>/`.

All asset and deck paths are relative, so it works whether the site is served from a domain root or a `/<repo-name>/` subpath.

## Project layout

```
index.html            # markup + Vue template
app.js                # Vue app: loading, selection, navigation
styles.css            # theme on top of Pico CSS
decks/manifest.json   # list of available decks
decks/*.json          # the decks themselves
```
