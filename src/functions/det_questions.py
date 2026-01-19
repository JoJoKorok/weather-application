from src.data.country_codes import prompt_country_code
from src.data.i18n import TEXT


def location_data(city_name=None, postal_code=None, country_code=None, interactive=True, lang: str = "en"):
    # Collect location input for the proxy weather call.
    # Returns: (city_name, postal_code, country_code)

    t = TEXT.get(lang, TEXT["en"])

    if not city_name and not postal_code:
        if interactive:
            city_name = input(t["enter_city_or_postal"]).strip()
            if not city_name:
                postal_code = input(t["enter_postal"]).strip()
        else:
            raise ValueError("A municipality name or postal code must be provided.")

    if not country_code:
        if interactive:
            # prompt_country_code returns alpha-2 (US/JP/etc)
            country_code = prompt_country_code(confirm=True, allow_fuzzy=True, lang=lang).lower()
        else:
            raise ValueError("country_code must be provided when interactive=False.")

    return city_name or None, postal_code or None, country_code
