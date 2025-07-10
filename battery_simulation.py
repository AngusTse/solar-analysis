import os
import pandas as pd
from datetime import datetime
from solaredge_api import SolarEdgeAPI
from battery_simulator import BatterySimulator

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

    # Get data from SolarEdge
    energy_data = api.get_energy_data(start_date, end_date)
    consumption_data = api.get_consumption_data(start_date, end_date)

    # Initialize simulator
    simulator = BatterySimulator(battery_capacity_kwh, battery_efficiency)
    
    # Process daily data
    results = []
    for prod, cons in zip(energy_data['energy']['values'], consumption_data['consumption']['values']):
        date = prod['date']
        prod_kwh = prod['value'] / 1000  # Convert Wh to kWh
        cons_kwh = cons['value'] / 1000

        # Simulate battery behavior
        charge, discharge, export, import_kwh = simulator.simulate_day(prod_kwh, cons_kwh)

        # Calculate costs
        cost_without = (import_kwh * grid_price_per_kwh) - (export * feed_in_tariff_per_kwh) + daily_connection_fee
        cost_with = (import_kwh * grid_price_per_kwh) + daily_connection_fee
        savings = cost_without - cost_with

        results.append({
            'date': date,
            'production_kwh': prod_kwh,
            'consumption_kwh': cons_kwh,
            'grid_import_kwh': import_kwh,
            'solar_export_kwh': export,
            'battery_charge_kwh': charge,
            'battery_discharge_kwh': discharge,
            'cost_without_battery': cost_without,
            'cost_with_battery': cost_with,
            'daily_savings': savings
        })

    # Export results
    df = pd.DataFrame(results)
    df.to_csv('battery_simulation_result.csv', index=False)
    return df

if __name__ == "__main__":
    simulation_params = {
        'start_date': "2023-01-01",
        'end_date': "2023-12-31",
        'grid_price_per_kwh': 0.40,
        'feed_in_tariff_per_kwh': 0.08,
        'battery_capacity_kwh': 10.0,
        'battery_efficiency': 0.90,
        'daily_connection_fee': 1.10
    }
    
    results = run_simulation(**simulation_params)
    print(f"Simulation complete. Results saved to battery_simulation_result.csv")
