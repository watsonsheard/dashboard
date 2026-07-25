# Watson Sheard — Personal Dashboard

A single, self-contained personal dashboard. No server to run or pay for — it's a
static page you host free on GitHub Pages and open by URL on any computer or phone.

## What it shows

- **Header** — your name + a live day / date / clock, and a light/dark theme toggle.
- **Metrics bar** — Steps, Active Calories, Distance, Sleep, Resting HR, Weight,
  each with a progress bar or trend (green = good). *(Currently mock data; wired to
  Garmin in Phase 2.)*
- **Calendar** — the current month with today highlighted + an events list.
  *(Live Google Calendar in Phase 3.)*
- **Referee — This Week** — your weekly games grouped by day with venue, level,
  position, pay, and driving, plus a weekly summary. *(Sample data; wired to your
  2026-season Google Sheet in Phase 2.)*
- **Weather** — **live** Minneapolis conditions + 5-day forecast via
  [Open-Meteo](https://open-meteo.com) (no API key).
- **Focus & Tasks** — a simple checklist saved in your browser (`localStorage`).

## Run it locally

Just open `index.html` in a browser — or, so the live weather fetch works cleanly,
serve the folder:

```bash
python -m http.server 8765
# then visit http://localhost:8765/index.html
```

## Design

Warm off-white ("tan") ground, pastel-blue accent, and semantic color
(green = good, amber = caution, red = behind). Fully responsive and theme-aware
(follows your OS light/dark, with a manual toggle that's remembered).

## Roadmap

| Phase | What | Status |
|---|---|---|
| 1 | Aesthetic shell + live weather + clock + tasks | ✅ done |
| 2 | Data robot: GitHub Actions fetches Garmin + referee Sheet → JSON | ⏳ next |
| 3 | Live Google Calendar (read-only, in-browser) | ⏳ |
| 4 | Deploy to GitHub Pages, iPhone "Add to Home Screen", polish | ⏳ |

## Structure

```
watson-dashboard/
├── index.html                     # the whole dashboard (self-contained)
├── data/                          # garmin.json + referee.json (written by the robot, Phase 2)
├── scripts/                       # fetch_data.py (the robot, Phase 2)
└── .github/workflows/             # update-data.yml — free cron (Phase 2)
```
