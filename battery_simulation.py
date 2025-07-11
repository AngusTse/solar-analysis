import os
import pandas as pd
from datetime import datetime
from solaredge_api import SolarEdgeAPI  # Fix module name: solaredge_api, not solarededge_api
from battery_simulator import BatterySimulator
from datetime import date

def run_simulation(
    start_date: str,
    end_date: str,
    grid_price_per_kwh: float,
    feed_in_tariff_per_kwh: float,
    battery_capacity_kwh: float,
    battery_efficiency: float,
    daily_connection_fee: float
):
    # Initialize API client
    api_key = os.getenv('SE_API_KEY')
    site_id = os.getenv('SE_SITE_ID')
    api = SolarEdgeAPI(api_key, site_id)

    def export_consumption_data_to_csv(consumption_data, filename='output/api_grouped_by_date.csv'):
        """Export API energyDetails meters to CSV grouped by date, with static column order."""
        meters = consumption_data['energyDetails']['meters']
        date_dict = {}
        meter_types = set()
        for meter in meters:
            meter_type = meter['type']
            meter_types.add(meter_type)
            for entry in meter['values']:
                date = entry['date']
                value = entry.get('value', None)
                if date not in date_dict:
                    date_dict[date] = {}
                date_dict[date][meter_type] = value
        # Define static column order
        static_columns = ['date', 'Production', 'Consumption', 'SelfConsumption', 'FeedIn', 'Purchased']
        # Add any extra meter types not in static_columns
        all_columns = static_columns + sorted(meter_types - set(static_columns))
        df_api = pd.DataFrame.from_dict(date_dict, orient='index')
        df_api.index.name = 'date'
        df_api = df_api.reset_index().sort_values('date')
        df_api = df_api.reindex(columns=all_columns)
        df_api.to_csv(filename, index=False)
        print(f"Exported API response to {filename}")

    try:
        consumption_data = api.get_energy_details(start_date, end_date)
    except Exception as e:
        print("Warning: Could not fetch energy details from SolarEdge API.")
        print(f"Error: {e}")


    export_consumption_data_to_csv(consumption_data)

    # Initialize simulator
    simulator = BatterySimulator(battery_capacity_kwh, battery_efficiency)
    results = []

    # Extract daily production and consumption from energyDetails
    if 'energyDetails' in consumption_data and 'meters' in consumption_data['energyDetails']:
        meter_map = {}
        for meter in consumption_data['energyDetails']['meters']:
            meter_type = meter.get('type')
            values = {v['date']: (v.get('value', 0) or 0) for v in meter.get('values', [])}
            meter_map[meter_type] = values

        # Use all dates from production data
        production_by_date = meter_map.get('Production', {})
        consumption_by_date = meter_map.get('Consumption', {})
        feed_in_by_date = meter_map.get('FeedIn', {})
        purchased_by_date = meter_map.get('Purchased', {})
        self_consumption_by_date = meter_map.get('SelfConsumption', {})

        for date in sorted(production_by_date.keys()):
            prod_kwh = (production_by_date.get(date, 0)) / 1000
            cons_kwh = (consumption_by_date.get(date, 0)) / 1000
            feed_in_kwh = (feed_in_by_date.get(date, 0)) / 1000
            purchased_kwh = (purchased_by_date.get(date, 0)) / 1000
            self_consumption_kwh = (self_consumption_by_date.get(date, 0)) / 1000

            # Simulate battery behavior
            charge, discharge, feed_in_kwh_battery, purchased_kwh_battery = simulator.simulate_day(feed_in_kwh, purchased_kwh)

            # Use FeedIn meter for feed-in without battery
            feed_in_without_battery = feed_in_kwh
            feed_in_earnings_without_battery = feed_in_without_battery * feed_in_tariff_per_kwh

            # Calculate grid import and cost without battery
            import_without_battery = purchased_kwh
            cost_import_without_battery = import_without_battery * grid_price_per_kwh + daily_connection_fee

            # Calculate costs with battery
            cost_without = (import_without_battery * grid_price_per_kwh) - (feed_in_kwh * feed_in_tariff_per_kwh) + daily_connection_fee
            cost_with = (purchased_kwh_battery * grid_price_per_kwh) - (feed_in_kwh_battery * feed_in_tariff_per_kwh)  + daily_connection_fee
            savings = cost_with - cost_without

            results.append({
                'date': date,
                'production_kwh': prod_kwh,
                'consumption_kwh': cons_kwh,
                'self_consumption_kwh': self_consumption_kwh,
                'import_from_grid_without_battery_kwh': import_without_battery,
                'import_from_grid_without_battery_cost': cost_import_without_battery,
                'feed_in_to_grid_without_battery_kwh': feed_in_without_battery,
                'feed_in_earnings_without_battery': feed_in_earnings_without_battery,
                'battery_grid_import_kwh': purchased_kwh_battery,
                'battery_solar_export_kwh': feed_in_kwh_battery,
                'battery_charge_kwh': charge,
                'battery_discharge_kwh': discharge,
                'cost_without_battery': cost_without,
                'cost_with_battery': cost_with,
                'battery_daily_savings': savings
            })
    else:
        print("No valid energy details or meters found in data.")

    # Export results
    df = pd.DataFrame(results)
    df = df.round(2)  # Round all numeric columns to 2 decimals
    df.to_csv('output/battery_simulation_result.csv', index=False)
    return df

if __name__ == "__main__":
    simulation_params = {
        'start_date': "2025-01-29",
        'end_date': date.today().strftime("%Y-%m-%d"),
        'grid_price_per_kwh': 0.344,
        'feed_in_tariff_per_kwh': 0.03,
        'battery_efficiency': 0.90,
        'daily_connection_fee': 0.898
    }

    battery_capacities = [6.0, 10.0, 15.0]  # Example capacities in kWh

    for capacity in battery_capacities:
        print(f"Running simulation for battery_capacity_kwh={capacity}")
        params = simulation_params.copy()
        params['battery_capacity_kwh'] = capacity
        df = run_simulation(**params)
        output_file = f"output/battery_simulation_result_{capacity}kwh.csv"
        df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")

    print("All simulations complete.")
