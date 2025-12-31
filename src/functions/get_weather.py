import os
import requests


def _get_proxy_url() -> str:
    # Retrieves the proxy API endpoint from environment variables.
    # This prevents hardcoding the proxy URL into the source code.

    DEFAULT_PROXY_URL = "https://weather-application-c7bh.onrender.com/weather"
    
    proxy_url = os.getenv("WEATHER_PROXY_URL", "").strip()

    return proxy_url if proxy_url else DEFAULT_PROXY_URL


    
def _get_proxy_headers() -> dict:
    
    # Builds optional headers for proxy authentication.
    # If a proxy token is provided, it is sent as a Bearer token.
    token = os.getenv("WEATHER_PROXY_TOKEN", "").strip()

    # Sends Bearer token only if provided
    return {"Authorization": f"Bearer {token}"} if token else {}


def get_weather_by_city_name(city_name, country_code):
    # Catches weather data for a parameter-passed city from the proxy API.

    # Retrieves proxy API endpoint
    BASE_URL = _get_proxy_url()

    # Parameters for API request
    params = {
        "city": city_name,
        "country": country_code.lower(),
        "units": "metric"
    }

    # Optional headers for proxy authentication
    headers = _get_proxy_headers()

    try:
        # GET request to proxy API
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=120)

        # Exception raised for bad status codes.
        response.raise_for_status()

        # Parse JSON response into python dictionary
        weather_data = response.json()

        # Extracts relevant info
        main_data = weather_data.get("main", {})
        area_name = weather_data.get("name")
        temperature = main_data.get("temp")
        humidity = main_data.get("humidity")
        wind_speed = weather_data.get("wind", {}).get("speed")
        description = weather_data.get("weather", [{}])[0].get("description")

        if temperature is not None and description is not None:
            print(f"\nWeather in {area_name}:")
            print(f"    Temperature: {temperature}°C")
            print(f"    Humidity: {humidity}%")
            print(f"    Wind Speed: {wind_speed} m/s")
            print(f"    Description: {description.capitalize()}")
        else:
            print(f"Could not retrieve complete weather data for {city_name}")

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            print(f"Error: City '{city_name}' not found.")
        elif response.status_code == 401:
            print("Error: Unauthorized proxy request. Check proxy token.")
        elif response.status_code == 429:
            print("Error: Proxy rate limit exceeded. Please try again later.")
        else:
            print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred during the API request: {req_err}")


def get_weather_by_postal_code(postal_code, country_code="us"):
    # Catches weather data for a parameter-passed postal code from the proxy API.

    # Retrieves proxy API endpoint
    BASE_URL = _get_proxy_url()

    # Parameters for API request
    params = {
        "postal": postal_code,
        "country": country_code.lower(),
        "units": "metric"
    }

    # Optional headers for proxy authentication
    headers = _get_proxy_headers()

    try:
        # GET request to proxy API
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=120)

        # Exception raised for bad status codes.
        response.raise_for_status()

        # Parse JSON response into python dictionary
        weather_data = response.json()

        # Extracts relevant info
        main_data = weather_data.get("main", {})
        area_name = weather_data.get("name")
        temperature = main_data.get("temp")
        humidity = main_data.get("humidity")
        wind_speed = weather_data.get("wind", {}).get("speed")
        description = weather_data.get("weather", [{}])[0].get("description")

        if temperature is not None and description is not None:
            print(f"\n\nWeather in {area_name} ({postal_code}, {country_code.upper()}):")
            print(f"    Temperature: {temperature}°C")
            print(f"    Humidity: {humidity}%")
            print(f"    Wind Speed: {wind_speed} m/s")
            print(f"    Description: {description.capitalize()}")
        else:
            print(f"Incomplete weather data retrieved for: {postal_code}, {country_code.upper()}")

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            print(f"Error: Postal code '{postal_code}, {country_code.upper()}' not found.")
        elif response.status_code == 401:
            print("Error: Unauthorized proxy request. Check proxy token.")
        elif response.status_code == 429:
            print("Error: Proxy rate limit exceeded. Please try again later.")
        else:
            print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred during the API request: {req_err}")
