from ..data.country_codes import prompt_country_code

def location_data(city_name=None, postal_code=None, country_code=None, interactive=True):
    """
    Collect location input for OpenWeatherMap.
    Returns: (city_name, postal_code, country_code)
    api_key is accepted for compatibility with the main program flow.
    This function only collects location input; it does not call the API.
    """

    if not city_name and not postal_code:
        if interactive:
            city_name = input("Enter a municipality name or press Enter to use a postal code: ").strip()
            if not city_name:
                postal_code = input("Enter a postal/ZIP code: ").strip()
        else:
            raise ValueError("A municipality name or postal code must be provided.")

    if not country_code:
        if interactive:
            country_code = prompt_country_code(confirm=True, allow_fuzzy=True).lower()
        else:
            raise ValueError("country_code must be provided when interactive=False.")

    return city_name or None, postal_code or None, country_code
