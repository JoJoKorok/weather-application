import os
import time
from collections import defaultdict, deque

import httpx
from fastapi import FastAPI, HTTPException, Request



"""
Enviroment Pulling Configuration
"""

# My OpeanWeatherMap API Key variable within Working OS Enviroment
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Takes env var and turns it into a set of allowed tokens.
PROXY_TOKENS = set(
    t.strip()
    for t in os.getenv("PROXY_TOKENS", "").split(",")
    if t.strip()
)

# Limits API calls allowed in env var, or defaults to 60 per minute.
OPENWEATHER_RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))

# Stores the endpoint of OpenWeatherMap's API
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# Starts an instance of the FastAPI class, registering data routes
# 'univron' requires an object to run, in this case, 'app'
app = FastAPI()

# Maps a key to a deque of timestamps if the key doesn't exist.
_hits = defaultdict(deque)



"""
Helper Functions
"""

# Function Definition that returns str or None
def _get_bearer_token(request: Request) -> str | None:
    
    # Looks for Authorization header, defaults to ""
    auth = request.headers.get("authorization", "")
    
    # Checks if header starts with "bearer ", case insensitive
    if auth.lower().startswith("bearer "):

        
        # Returns a split into a minimum of 2 parts, token section and removes and extra sections.
        return auth.split(" ", 1)[1].strip()
    
    # No valid Bearer format, returns None
    return None

# Function Definition that returns None
# key = str; idetifier per token or per IP
# limit = int; max allowed requests per minute 
def _enforce_rate_limit(key: str, limit: int) -> None:
    
    # Current UNIX time in seconds as a float
    now = time.time()
    
    # The earliest starting time within the last minute
    window_start = now - 60
    
    # Retrieves the deque for this key
    # If missing, defaultdict(deque) creates an empty deque
    q = _hits[key]
    
    # While loop removing timestamps older than 60 from q
    # starts with q[0], oldest timestamp in q
    # Removes from the left of the deque (popleft())
    while q and q[0] < window_start:
        q.popleft()
    
    # Checks if the length of q is greater than or equal to the set limit.
    if len(q) >= limit:
        # Raises an exception for the standard "Too Many Requests." code number, 429.
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    
    q.append(now)



"""
API Endpoint
"""

# Basic root endpoint for sanity checks and uptime monitors.
@app.get("/")
async def root():
    return {"status": "ok", "hint": "Use /weather"}

# Decorator (function abstraction) for FastAPT to handle GET requests to "/weather".
@app.get("/weather")

# Async function for FastAPT
async def weather(
    #Takes REQUEST object
    request: Request,
    
    # Optional query params w/ defaults to None if none.
    city: str | None = None,
    postal: str | None = None,
    
    # Optional query params w/ hardcoded defaults. 
    country: str = "us",
    units: str = "metric"
):

    # Checks if nothing is retrieved for secret key in env vars.
    if not OPENWEATHER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Server missing OPENWEATHER_API_KEY",
        )

    
    # Extracts token from header
    token = _get_bearer_token(request)

    
    # Checks if an allowed token(s) has been configured
    # Raises 401 Exception, needing valid credentials.
    if PROXY_TOKENS:
        if not token or token not in PROXY_TOKENS:
            raise HTTPException(status_code=401, detail="Unauthorized")

    # Assigns current client IP to 'client_ip'    
    client_ip = request.client.host if request.client else "unknown"

    # Assigns key for rate limiting
    # If a token exists, it assigns it as rate limit/token
    # Otherwise, it assigns it as rate limit/IP
    rate_key = f"tok:{token}" if token else f"ip{client_ip}"

    # Enactment of rate limit on current user, prevents spamming
    _enforce_rate_limit(rate_key, OPENWEATHER_RATE_LIMIT_PER_MIN)

    # Normalizes country code for OpenWeather
    country = country.strip().upper()

    # Parameters for OpenWeather API request
    params = {
        "appid": OPENWEATHER_API_KEY,
        "units": units
    }

    # Uses city search if provided
    if city:
        params["q"] = f"{city.strip()},{country}"

    # Uses postal search if provided
    elif postal:
        params["zip"] = f"{postal.strip()},{country}"

    # Otherwise request is invalid
    else:
        raise HTTPException(
            status_code=400, 
            detail="Provide either city or postal"
            )

        
    # Calls OpenWeatherMap with an async HTTP client with an 8-second timeout.
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get(OPENWEATHER_URL, params=params)
        
    # Checks OpenWeatherMap Call response code for failure codes.
    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise HTTPException(
            status_code=response.status_code, 
            detail=detail
            )
    
    # Parses response body into a dict/list structure.
    data = response.json()
    
    # Returns a dict with all nessecary fields for client.
    # FastAPI serializes this dict to a JSON for HTTP response automatically.
    return {
        "name": data.get("name"),
        "sys": data.get("sys"),
        "main": data.get("main"),
        "wind": data.get("wind"),
        "weather": data.get("weather"),
    }
    
    
    
    
        
        


