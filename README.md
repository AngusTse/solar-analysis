# Solar Analysis

This project provides tools for simulating and analyzing solar and battery savings using your SolarEdge data. You can use either a web interface or run simulations directly in the terminal.

## Features
- Input simulation parameters (dates, prices, battery size, efficiency, cost, etc.)
- Run battery savings simulation
- View summary statistics and financial analysis
- Interactive charts (Chart.js) for daily and monthly trends (web app)
- Paginated results table (web app)
- Export results to CSV (terminal and web app)

## Setup

### 1. Clone the repository
```bash
git clone <repo-url>
cd solar-analysis
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up SolarEdge API credentials
Export your SolarEdge API key and site ID as environment variables:
```bash
export SE_API_KEY=your_solaredge_api_key
export SE_SITE_ID=your_solaredge_site_id
```

You can add these lines to your `.env` or shell profile for convenience.

---

## Running the Web App

The web app provides a user-friendly interface for running simulations, viewing summaries, and exploring interactive charts.

```bash
venv/bin/python app.py
```

- Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.
- Enter or adjust the simulation parameters (dates, prices, battery size, battery cost, etc.).
- Click **Run Simulation**.
- View the summary, charts, and paginated results table.

---

## Running the Simulation in the Terminal

You can also run the simulation directly from the terminal and export results to CSV.

```bash
venv/bin/python battery_simulation.py
```

- Adjust simulation parameters in `battery_simulation.py` as needed.
- Results will be saved to the `output/` directory as CSV files.

---

## Notes
- The app fetches data from the SolarEdge API for the specified date range.
- All charting in the web app is done in the browser using Chart.js (no server-side plotting required).
- You can adjust the battery cost to reflect your actual or quoted price.

## Requirements
- Python 3.8+
- Flask
- pandas
- Chart.js (included via CDN in the template)

## Troubleshooting
- If you see errors about missing API keys, ensure you have set `SE_API_KEY` and `SE_SITE_ID` in your environment.
- If you change code, restart the Flask server to see updates.

---

For questions or issues, please open an issue in this repository.
