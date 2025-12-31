import pycountry

def resolve_country(user_text: str, allow_fuzzy: bool = True):
    s = (user_text or "").strip()
    if not s:
        return None, []

    u = s.upper()

    if len(u) == 2:
        c = pycountry.countries.get(alpha_2=u)
        if c:
            return c, [c]

    if len(u) == 3:
        c = pycountry.countries.get(alpha_3=u)
        if c:
            return c, [c]

    for c in pycountry.countries:
        if c.name.lower() == s.lower():
            return c, [c]

    if allow_fuzzy:
        try:
            matches = pycountry.countries.search_fuzzy(s)
            return matches[0], matches[:5]
        except LookupError:
            pass

    return None, []

def prompt_country_code(confirm: bool = True, allow_fuzzy: bool = True) -> str:
    while True:
        raw = input("Enter country (name, alpha-2, or alpha-3): ").strip()
        best, candidates = resolve_country(raw, allow_fuzzy=allow_fuzzy)

        if not best:
            print("No country found. Try 'United States', 'US', 'USA', 'Japan', 'JP', etc.\n")
            continue

        if len(candidates) > 1:
            print("\nPossible matches:")
            for i, c in enumerate(candidates, start=1):
                print(f"  {i}) {c.name} [{c.alpha_2}/{c.alpha_3}]")
            choice = input("Select a number (or press Enter for #1): ").strip()
            if choice:
                try:
                    best = candidates[int(choice) - 1]
                except (ValueError, IndexError):
                    print("Invalid selection. Try again.\n")
                    continue

        alpha2 = best.alpha_2

        if confirm:
            yn = input(f"Use '{best.name}' ({alpha2})? [y/n]: ").strip().lower()
            if yn not in ("y", "yes"):
                print("Okay — try again.\n")
                continue

        return alpha2
