import pycountry
from src.data.i18n import TEXT


def resolve_country(user_text: str, allow_fuzzy: bool = True):
    # Tries to resolve user input into a pycountry country object.
    # Returns: (best_match | None, candidates_list)

    s = (user_text or "").strip()
    if not s:
        return None, []

    u = s.upper()

    # alpha-2 match
    if len(u) == 2:
        c = pycountry.countries.get(alpha_2=u)
        if c:
            return c, [c]

    # alpha-3 match
    if len(u) == 3:
        c = pycountry.countries.get(alpha_3=u)
        if c:
            return c, [c]

    # exact name match
    for c in pycountry.countries:
        if c.name.lower() == s.lower():
            return c, [c]

    # fuzzy fallback (pycountry built-in)
    if allow_fuzzy:
        try:
            matches = pycountry.countries.search_fuzzy(s)
            return matches[0], matches[:5]
        except LookupError:
            pass

    return None, []


def prompt_country_code(confirm: bool = True, allow_fuzzy: bool = True, lang: str = "en") -> str:
    # Interactive country prompt.
    # Returns alpha-2 code (lowercase handled by caller if desired).

    lang = (lang or "en").strip().lower()
    if lang not in ("en", "ja"):
        lang = "en"

    t = TEXT.get(lang, TEXT["en"])

    while True:
        raw = input(t["enter_country"]).strip()
        best, candidates = resolve_country(raw, allow_fuzzy=allow_fuzzy)

        if not best:
            print(t["no_country_found"])
            continue

        if len(candidates) > 1:
            print(t["possible_matches"])
            for i, c in enumerate(candidates, start=1):
                print(f"  {i}) {c.name} [{c.alpha_2}/{c.alpha_3}]")

            choice = input(t["select_number"]).strip()
            if choice:
                try:
                    best = candidates[int(choice) - 1]
                except (ValueError, IndexError):
                    print(t["invalid_selection"])
                    continue

        alpha2 = best.alpha_2

        if confirm:
            yn = input(t["confirm_country"].format(name=best.name, code=alpha2)).strip().lower()
            if yn not in ("y", "yes"):
                print(t["try_again"])
                continue

        return alpha2
