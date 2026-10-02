import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

def get_hourly_data_string():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 46.0569,
        "longitude": 14.5058,
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"],
        "timezone": "auto",
        "start_date": "2026-08-16",
        "end_date": "2026-08-16",
    }
    responses = openmeteo.weather_api(url, params = params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        ).tz_convert(response.Timezone().decode())
    }

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    # hourly_dataframe = pd.DataFrame(data = hourly_data)
    # print("\nHourly data\n", hourly_dataframe)

    # Returns a string with weather data for the morning mid day and night
    morning_index = 6
    midday_index = 12
    night_index = 21
    end_index = 23

    result = "Weather data:\n"
    result += f"Morning (06:00): Temperature: {hourly_data['temperature_2m'][morning_index]:.2f}°C, Humidity: {hourly_data['relative_humidity_2m'][morning_index]:.2f}%, Precipitation: {hourly_data['precipitation'][morning_index]:.2f}mm, Wind Speed: {hourly_data['wind_speed_10m'][morning_index]:.2f}m/s\n"
    result += f"Midday (12:00): Temperature: {hourly_data['temperature_2m'][midday_index]:.2f}°C, Humidity: {hourly_data['relative_humidity_2m'][midday_index]:.2f}%, Precipitation: {hourly_data['precipitation'][midday_index]:.2f}mm, Wind Speed: {hourly_data['wind_speed_10m'][midday_index]:.2f}m/s\n"
    result += f"Night (21:00): Temperature: {hourly_data['temperature_2m'][night_index]:.2f}°C, Humidity: {hourly_data['relative_humidity_2m'][night_index]:.2f}%, Precipitation: {hourly_data['precipitation'][night_index]:.2f}mm, Wind Speed: {hourly_data['wind_speed_10m'][night_index]:.2f}m/s\n"
    result += f"End of day (24:00): Temperature: {hourly_data['temperature_2m'][end_index]:.2f}°C, Humidity: {hourly_data['relative_humidity_2m'][end_index]:.2f}%, Precipitation: {hourly_data['precipitation'][end_index]:.2f}mm, Wind Speed: {hourly_data['wind_speed_10m'][end_index]:.2f}m/s\n"
    result += f"Daily Max Temperature: {daily_temperature_2m_max[0]:.2f}°C, Daily Min Temperature: {daily_temperature_2m_min[0]:.2f}°C\n"
    return result

# Example usage:
print(get_hourly_data_string())