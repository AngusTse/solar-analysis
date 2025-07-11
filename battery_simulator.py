from dotenv import load_dotenv
load_dotenv()

class BatterySimulator:
    def __init__(self, capacity_kwh: float, efficiency: float):
        self.capacity_kwh = capacity_kwh
        self.efficiency = efficiency
        self.current_charge = 0.0

    def simulate_day(self, feed_in_kwh: float, purchased_in_kwh: float) -> tuple:
        excess_solar = feed_in_kwh # max(0, production_kwh - consumption_kwh)
        energy_deficit = purchased_in_kwh  # max(0, consumption_kwh - production_kwh)
        
        # Charge from excess solar
        charge = min(excess_solar, self.capacity_kwh - self.current_charge) * self.efficiency
        remaining_excess = excess_solar - (charge / self.efficiency)
        self.current_charge += charge

        # Discharge to meet deficit
        max_discharge = min(energy_deficit, self.current_charge)
        self.current_charge -= max_discharge
        remaining_deficit = energy_deficit - max_discharge

        return (charge, max_discharge, remaining_excess, remaining_deficit)
