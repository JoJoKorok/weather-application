def test_import_client_dependencies():
    # Confirms core client dependencies are installed.
    import requests
    import pycountry
    assert requests is not None
    assert pycountry is not None


def test_import_proxy_dependencies():
    # Confirms proxy dependencies are installed (needed if you run proxy tests locally).
    import fastapi
    import httpx
    import uvicorn
    assert fastapi is not None
    assert httpx is not None
    assert uvicorn is not None
