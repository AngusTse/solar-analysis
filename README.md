# Solar Battery Simulation

Simulate solar battery usage using SolarEdge API data and export daily analysis results to a CSV file.

## Setup Instructions (macOS)

1. **Install Python 3.9+**  
   It's recommended to use Homebrew:
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install python
   ```

2. **Clone this repository and navigate to the project folder**
   ```sh
   cd /path/to/solar-analysis
   ```

3. **Create and activate a virtual environment**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install required libraries**
   ```sh
   pip install pandas requests
   ```

5. **Set your SolarEdge API key and site ID as environment variables**  
   You can either add the following lines to your `~/.bash_profile`, `~/.zshrc`, or create a `.env` file in the project directory:

   **Option 1: Shell profile**
   ```sh
   export SE_API_KEY="your_api_key"
   export SE_SITE_ID="your_site_id"
   ```
   Then reload your shell or source the file:
   ```sh
   source ~/.bash_profile
   # or
   source ~/.zshrc
   ```

   **Option 2: .env file**  
   Create a file named `.env` in the project directory with the following content:
   ```
   SE_API_KEY=your_api_key
   SE_SITE_ID=your_site_id
   ```

   If using a `.env` file, install the `python-dotenv` package:
   ```sh
   pip install python-dotenv
   ```
   And add the following to the top of `battery_simulation.py`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

6. **Run the simulation**
   ```sh
   python battery_simulation.py
   ```

## Input Parameters

You can adjust simulation parameters in `battery_simulation.py`:
- `start_date`, `end_date`: Date range (YYYY-MM-DD)
- `grid_price_per_kwh`: Grid electricity price (e.g., 0.40)
- `feed_in_tariff_per_kwh`: Solar export tariff (e.g., 0.08)
- `battery_capacity_kwh`: Usable battery capacity (e.g., 10.0)
- `battery_efficiency`: Battery round-trip efficiency (e.g., 0.90)
- `daily_connection_fee`: Daily grid connection fee (e.g., 1.10)

## Output

Results are saved to `battery_simulation_result.csv` with columns:
- date, production_kwh, consumption_kwh, grid_import_kwh, solar_export_kwh, battery_charge_kwh, battery_discharge_kwh, cost_without_battery, cost_with_battery, daily_savings

---
