import requests
from datetime import datetime

class SolarEdgeAPI:
    BASE_URL = "https://monitoringapi.solaredge.com"

    def __init__(self, api_key: str, site_id: str):
        self.api_key = api_key
        self.site_id = site_id

    def _make_request(self, endpoint: str, params: dict) -> dict:
        url = f"{self.BASE_URL}/site/{self.site_id}/{endpoint}"
        params['api_key'] = self.api_key
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_energy_data(self, start_date: str, end_date: str) -> dict:
        # Ensure dates are in YYYY-MM-DD format
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%Y-%m-%d")
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%Y-%m-%d")
        return self._make_request("energy", {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": "DAY"
        })

    def get_energy_details(self, start_date: str, end_date: str) -> dict:
        # Ensure dates are in YYYY-MM-DD format
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%Y-%m-%d")
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%Y-%m-%d")
        return self._make_request("energyDetails", {
            "startTime": start_date + " 00:00:00",
            "endTime": end_date + " 23:59:59",
            "timeUnit": "DAY"
        })
