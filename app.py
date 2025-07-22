from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import date
from battery_simulation import run_simulation
import os
import io
import json

app = Flask(__name__)

# Default parameters
DEFAULTS = {
    'start_date': "2025-01-29",
    'end_date': date.today().strftime("%Y-%m-%d"),
    'grid_price_per_kwh': 0.344,
    'feed_in_tariff_per_kwh': 0.03,
    'battery_capacity_kwh': 10.0,
    'battery_efficiency': 0.90,
    'daily_connection_fee': 0.898,
    'battery_cost': 10000  # Default: $10,000
}

RESULTS_PER_PAGE = 10

@app.route('/', methods=['GET', 'POST'])
def index():
    params = DEFAULTS.copy()
    results = None
    summary = None
    chart_data = None
    page = int(request.args.get('page', 1))
    total_pages = 1
    if request.method == 'POST':
        for key in params:
            if key in request.form:
                value = request.form[key]
                if key in ['grid_price_per_kwh', 'feed_in_tariff_per_kwh', 'battery_capacity_kwh', 'battery_efficiency', 'daily_connection_fee', 'battery_cost']:
                    value = float(value)
                params[key] = value
        df = run_simulation(
            params['start_date'],
            params['end_date'],
            params['grid_price_per_kwh'],
            params['feed_in_tariff_per_kwh'],
            params['battery_capacity_kwh'],
            params['battery_efficiency'],
            params['daily_connection_fee']
        )
        results = df.to_dict(orient='records')
        summary = get_summary(df, params)
        chart_data = df.to_json(orient='records')
        total_pages = (len(results) + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        start = (page - 1) * RESULTS_PER_PAGE
        end = start + RESULTS_PER_PAGE
        paginated_results = results[start:end]
    else:
        paginated_results = None
    return render_template('index.html', params=params, results=paginated_results, summary=summary, page=page, total_pages=total_pages, chart_data=chart_data)

def get_summary(df, params):
    # Data Summary
    total_days = len(df)
    date_range = f"{df['date'].iloc[0]} to {df['date'].iloc[-1]}"
    avg_daily_prod = df['production_kwh'].mean()
    total_prod = df['production_kwh'].sum()
    # Daily Energy Flow (No Battery)
    avg_grid_purchase = df['import_from_grid_without_battery_kwh'].mean()
    avg_feed_in = df['feed_in_to_grid_without_battery_kwh'].mean()
    avg_net_cost = df['cost_without_battery'].mean()
    avg_self_consumption = df['self_consumption_kwh'].mean() / avg_daily_prod if avg_daily_prod else 0
    # Battery Performance
    avg_grid_purchase_batt = df['battery_grid_import_kwh'].mean()
    avg_charge = df['battery_charge_kwh'].mean()
    avg_discharge = df['battery_discharge_kwh'].mean()
    avg_utilization = avg_discharge / params['battery_capacity_kwh'] if params['battery_capacity_kwh'] else 0
    avg_savings = df['battery_daily_savings'].mean()
    # Financial
    annual_savings_no_batt = df['cost_without_battery'].sum() * 365 / total_days
    annual_savings_with_batt = df['cost_with_battery'].sum() * 365 / total_days
    additional_annual_savings = annual_savings_no_batt - annual_savings_with_batt
    battery_cost = params.get('battery_cost', params['battery_capacity_kwh'] * 1000)
    payback_period = battery_cost / additional_annual_savings if additional_annual_savings else None
    annual_roi = (additional_annual_savings / battery_cost) * 100 if battery_cost else 0
    return {
        'total_days': total_days,
        'date_range': date_range,
        'avg_daily_prod': avg_daily_prod,
        'total_prod': total_prod,
        'avg_grid_purchase': avg_grid_purchase,
        'avg_feed_in': avg_feed_in,
        'avg_net_cost': avg_net_cost,
        'avg_self_consumption': avg_self_consumption,
        'avg_grid_purchase_batt': avg_grid_purchase_batt,
        'avg_charge': avg_charge,
        'avg_discharge': avg_discharge,
        'avg_utilization': avg_utilization,
        'avg_savings': avg_savings,
        'annual_savings_no_batt': annual_savings_no_batt,
        'annual_savings_with_batt': annual_savings_with_batt,
        'additional_annual_savings': additional_annual_savings,
        'payback_period': payback_period,
        'annual_roi': annual_roi
    }

if __name__ == '__main__':
    app.run(debug=True) 