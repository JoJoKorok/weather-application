import pycountry


def resolve_country(user_text: str, allow_fuzzy: bool = True):
    # Attempts to resolve a country from user input.
    # Accepts full country names, ISO alpha-2, ISO alpha-3, and optionally fuzzy matches.
    # Returns:
    #   - best match (pycountry Country object) or None
    #   - list of candidate matches (for user confirmation / display)

    # Normalizes input to a stripped string, defaults to empty if None
    s = (user_text or "").strip()
    if not s:
        return None, []

    # Uppercase version used for ISO code comparisons
    u = s.upper()

    # Checks for ISO 3166-1 alpha-2 code (e.g., "US", "JP")
    if len(u) == 2:
        c = pycountry.countries.get(alpha_2=u)
        if c:
            return c, [c]

    # Checks for ISO 3166-1 alpha-3 code (e.g., "USA", "JPN")
    if len(u) == 3:
        c = pycountry.countries.get(alpha_3=u)
        if c:
            return c, [c]

    # Attempts exact country name match (case-insensitive)
    for c in pycountry.countries:
        if c.name.lower() == s.lower():
            return c, [c]

    # Uses fuzzy search if enabled (handles misspellings and partial names)
    if allow_fuzzy:
        try:
            matches = pycountry.countries.search_fuzzy(s)
            # Returns best match first, plus up to 5 candidates for user selection
            return matches[0], matches[:5]
        except LookupError:
            # No fuzzy matches found
            pass

    # No valid country resolved
    return None, []


def prompt_country_code(confirm: bool = True, allow_fuzzy: bool = True) -> str:
    # Interactively prompts the user to select a country.
    # Accepts name, alpha-2, or alpha-3 input.
    # Always returns a confirmed ISO 3166-1 alpha-2 country code.

    while True:
        # Prompts user for country input
        raw = input("Enter country (name, alpha-2, or alpha-3): ").strip()

        # Attempts to resolve input into a country match
        best, candidates = resolve_country(raw, allow_fuzzy=allow_fuzzy)

        # No match found — restart prompt
        if not best:
            print("No country found. Try 'United States', 'US', 'USA', 'Japan', 'JP', etc.\n")
            continue

        # If multiple possible matches exist, present options to the user
        if len(candidates) > 1:
            print("\nPossible matches:")
            for i, c in enumerate(candidates, start=1):
                print(f"  {i}) {c.name} [{c.alpha_2}/{c.alpha_3}]")

            # Allows user to select a specific candidate
            choice = input("Select a number (or press Enter for #1): ").strip()
            if choice:
                try:
                    best = candidates[int(choice) - 1]
                except (ValueError, IndexError):
                    print("Invalid selection. Try again.\n")
                    continue

        # Extracts ISO alpha-2 code for downstream API usage
        alpha2 = best.alpha_2

        # Optional confirmation step before returning result
        if confirm:
            yn = input(f"Use '{best.name}' ({alpha2})? [y/n]: ").strip().lower()
            if yn not in ("y", "yes"):
                print("Okay — try again.\n")
                continue

        # Returns confirmed country code
        return alpha2
