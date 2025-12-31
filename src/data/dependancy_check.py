from __future__ import annotations
from importlib import import_module
import requests, sys, subprocess

"""
Dependency checks for optional/required packages.

Note on "updated":
- Without querying PyPI (internet), you can't know the absolute latest version.
- So we define "updated" as: meets a minimum required version.
"""

try:
    # Python 3.8+
    from importlib.metadata import version as pkg_version, PackageNotFoundError
except Exception:  # pragma: no cover
    # Very old Python fallback (unlikely)
    pkg_version = None
    PackageNotFoundError = Exception


def _run_pip(args: list[str]) -> None:
    """Run pip using the current Python interpreter."""
    subprocess.check_call([sys.executable, "-m", "pip", *args])


def _parse_version(v: str):
    """Parse versions safely; prefers packaging if available."""
    try:
        from packaging.version import Version
        return Version(v)
    except Exception:
        # Fallback: simple tuple parse (less accurate but works for basic x.y.z)
        parts = []
        for p in v.split("."):
            try:
                parts.append(int(p))
            except ValueError:
                # strip non-numeric tail (e.g., '1rc1')
                num = ""
                for ch in p:
                    if ch.isdigit():
                        num += ch
                    else:
                        break
                parts.append(int(num) if num else 0)
        return tuple(parts)


def ensure_pycountry(
    *,
    min_version: str | None = None,
    auto_install: bool = False,
    auto_upgrade: bool = False,
    quiet: bool = True,
) -> tuple[bool, str | None]:
    """
    Ensure pycountry is available and (optionally) meets a minimum version.

    Returns: (ok, installed_version)

    - If pycountry is missing:
        - auto_install=True will attempt: pip install pycountry
        - otherwise returns (False, None)
    - If min_version is provided and pycountry is older:
        - auto_upgrade=True will attempt: pip install -U pycountry
        - otherwise returns (False, installed_version)
    """
    installed = None

    # 1) Check installed
    try:
        import_module("pycountry")
    except ModuleNotFoundError:
        if auto_install:
            if not quiet:
                print("pycountry not found. Installing...")
            _run_pip(["install", "pycountry"])
            import_module("pycountry")
        else:
            return False, None

    # 2) Get version
    if pkg_version is not None:
        try:
            installed = pkg_version("pycountry")
        except PackageNotFoundError:
            # Installed via unusual means; still usable, but version unknown
            installed = None

    # 3) Compare with minimum required version
    if min_version and installed:
        if _parse_version(installed) < _parse_version(min_version):
            if auto_upgrade:
                if not quiet:
                    print(f"pycountry {installed} < {min_version}. Upgrading...")
                _run_pip(["install", "-U", "pycountry"])
                installed = pkg_version("pycountry")
            else:
                return False, installed

    return True, installed