from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from pydantic import BaseModel
import requests

templates = Jinja2Templates(directory="templates")

COUNTRIES_API="https://studies.cs.helsinki.fi/restcountries/api/all"
WEATHER_API="https://api.open-meteo.com/v1/forecast"
SUCCESS_STATUS=200

class CountryData(BaseModel):
    name: str
    capital: str
    region: str
    lat: float
    lng: float

class WeatherData(BaseModel):
    temperature: float
    wind_speed: float

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("base.html", { "request": request })

@app.get("/api/countries", response_model=list[CountryData])
async def list_countries(request: Request):
    response = requests.get(COUNTRIES_API)
    if response.status_code != SUCCESS_STATUS:
        raise HTTPException(status_code=500, detail="Error retrieving country list")
    countries = response.json()
    countriesData = []
    for country in countries:
        lat, lng = country["latlng"]
        countriesData.append(CountryData(name=country["name"]["official"], capital=country.get("capital", [""])[0], region=country["region"], lat=lat, lng=lng))

    # countriesData = [
    #     CountryData(name=country["name"]["official"], capital=country.get("capital", [""])[0], region=country["region"], lat=country["latlng"][0], lng=country["latlng"][1]) for country in countries
    # ]
    return templates.TemplateResponse(request, "countries.html", { "countries": countriesData })

@app.get("/api/countries/{capital}/weather")
async def weather_in_capital(request: Request, capital: str, country: str, lat: float, lng: float):
    response = requests.get(f"{WEATHER_API}?latitude={lat}&longitude={lng}&current_weather=true")
    if response.status_code != SUCCESS_STATUS:
        raise HTTPException(status_code=500, detail="Unable to retrieve weather data")
    weather_data = response.json()
    return templates.TemplateResponse(request, "weather.html", {
        "country": country,
        "capital": capital,
        "weather": {
            "temperature": weather_data["current_weather"]["temperature"],
            "wind_speed": weather_data["current_weather"]["windspeed"],
        }
    })