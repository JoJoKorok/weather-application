import requests
from functions.det_questions import location_data
from functions.get_weather import get_weather_by_city_name, get_weather_by_postal_code

if __name__ == "__main__":
    
    city, postal, country = location_data(interactive=True)

    if postal:
        get_weather_by_postal_code(postal, country_code=country)
    else:
        get_weather_by_city_name(city, country_code=country)
