# Pitch Arsenal Visualizer

An interactive baseball analytics tool that lets users explore any MLB pitcher's repertoire through Statcast data — pitch movement, velocity, spin, location, count usage, and platoon splits — all in one editorial-style dashboard.

🔗 **Live app:** [pitch-arsenal-visualizer.streamlit.app](https://pitch-arsenal-visualizer.streamlit.app)
✍️ **Built by:** [Jack Turek](https://jackturek708.com)

---

## What It Does

Search any active MLB pitcher and get a full visual breakdown of their arsenal:

- **Movement profile** — horizontal vs. vertical break for every pitch type, sized by usage and labeled with whiff rates on hover
- **Pitch mix** — usage percentages across the arsenal
- **Velocity & spin distributions** — full shape of the data, not just averages
- **Count-based usage** — how pitch selection shifts from 0-0 to 3-2
- **Handedness splits** — usage and whiff rates vs. LHH and RHH
- **Pitch location heatmaps** — catcher's POV, filterable by count
- **Pitcher vs. pitcher comparison** — side-by-side analysis of two pitchers (or the same pitcher across two seasons)

---

## Why This Tool Exists

Baseball Savant has the data. FanGraphs has the leaderboards. What's missing is the layer in between — a tool built around a question, with a point of view, that surfaces the *contrasts* that actually tell you something.

This app is built to live alongside written analysis. The goal isn't to replace Savant; it's to make the kinds of comparisons (pitcher A vs. pitcher B, this season vs. last, vs. lefties vs. righties, in 0-0 vs. 1-2 counts) that Savant doesn't streamline.

---

## Tech Stack

- **Streamlit** — Python web app framework
- **pybaseball** — Statcast data scraper
- **pandas** — data manipulation
- **Plotly** — interactive charts
- **Streamlit Community Cloud** — free hosting

---

## Project Structure

```
pitch_arsenal_visualizer/
├── .streamlit/
│   └── config.toml           # Editorial theme (cream + oxblood palette)
├── utils/
│   ├── data.py               # Statcast fetching, cleaning, summary stats
│   └── plots.py              # All Plotly chart functions
├── app.py                    # Streamlit UI — single + comparison tabs
├── requirements.txt
└── README.md
```

---

## Run Locally

```bash
git clone https://github.com/JTurek708/baseball.git
cd baseball/pitch_arsenal_visualizer

python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens automatically in your browser at `http://localhost:8501`.

---

## Design Notes

The visual identity is intentionally editorial — Playfair Display headers, Lora body text, a cream-and-oxblood palette borrowed from vintage baseball almanacs. Most analytics tools default to a generic dark dashboard look. This one tries to feel like it belongs in a publication.

---

## Roadmap

Future additions under consideration:

- Daily-updating homepage highlighting standout pitching performances
- Pitcher similarity finder (find a pitcher's closest historical comps)
- Season trajectory tracker (rolling metrics across a season)
- Stuff+ / Location grade dashboard

---

## Data Source

All data is pulled live from [Baseball Savant](https://baseballsavant.mlb.com/) via the [`pybaseball`](https://github.com/jldbc/pybaseball) library. Data updates daily during the MLB season.

---

## License

MIT
