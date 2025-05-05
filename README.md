# GPX Max. Speed Simulation

This Python script processes `.gpx` track files to analyze and visualize travel speeds, compare them against a configurable maximum speed (`vmax`), and calculate how much longer a trip would take if that speed limit were strictly followed.

## Features

- Parses all `.gpx` files in a `data/` folder
- Crops the track to a configurable bounding box (optional)
- Computes actual speeds between GPS points
- Identifies segments exceeding `vmax` and calculates the extra travel time required to obey the limit
- Generates optional plots:
  - Original vs adjusted speed traces
  - Highlights segments exceeding `vmax`
- Summarizes delays per file and overall

## Installation

Create a virtual environment and install the requirements:

```bash
python -m venv venv
source venv/bin/activate  # or venv\\Scripts\\activate on Windows
pip install -r requirements.txt
```
Rund the scriply by executing the main file: `python main.py`
