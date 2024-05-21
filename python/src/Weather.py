import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
import datetime
import json

class Weather:
    def __init__(self, past_days=3, cache_duration=3600):
        self.cache_session = requests_cache.CachedSession(
            '.cache', expire_after=cache_duration)
        self.retry_session = retry(
            self.cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)
        self.past_days = past_days
        self.api_url = "https://api.open-meteo.com/v1/forecast"
        self.tracking_parameters = [
            "temperature_2m",
            "relative_humidity_2m",
            "soil_temperature_0cm",
            "soil_temperature_6cm",
            "soil_moisture_0_to_1cm",
            "soil_moisture_1_to_3cm",
            "soil_moisture_3_to_9cm",
            "uv_index"
        ]

    def weather_request(self, location: tuple[float, float], timestamp: datetime.datetime):
        params = {
            "latitude": location[0],
            "longitude": location[1],
            "hourly": self.tracking_parameters,
            "wind_speed_unit": "ms",
            "timeformat": "unixtime",
            "timezone": "auto",
            "start_date": (timestamp-pd.Timedelta(days=self.past_days)).strftime("%Y-%m-%d"),
            "end_date": timestamp.strftime("%Y-%m-%d")
        }
        try:
            responses = self.openmeteo.weather_api(self.api_url, params=params)
            response = responses[0]
            hourly = response.Hourly()
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                ),
                "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
                "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
                "soil_temperature_0cm": hourly.Variables(2).ValuesAsNumpy(),
                "soil_temperature_6cm": hourly.Variables(3).ValuesAsNumpy(),
                "soil_moisture_0_to_1cm": hourly.Variables(4).ValuesAsNumpy(),
                "soil_moisture_1_to_3cm": hourly.Variables(5).ValuesAsNumpy(),
                "soil_moisture_3_to_9cm": hourly.Variables(6).ValuesAsNumpy(),
                "uv_index": hourly.Variables(7).ValuesAsNumpy()
            }
            hourly_dataframe = pd.DataFrame(data=hourly_data)
            return hourly_dataframe.to_json()
        except ConnectionError as e:  # for offline testing
            return None
