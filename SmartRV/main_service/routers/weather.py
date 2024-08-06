import datetime

from typing import Optional, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel, Field


router = APIRouter(
    prefix='/geo',
    tags=['GEO']
)


class Fact(BaseModel):
    text: str


class Location(BaseModel):
    latitude: float
    longitude: float
    
    city: Optional[str]
    county: Optional[str]
    country: Optional[str]
    
    facts: Optional[List[Fact]]


class Weather(BaseModel):
    date_time: Optional[datetime.datetime]
    temp_high: int
    temp_low: int
    humidity: int
    
    # TODO: Get other types based on weather service API


class WeatherResponse(BaseModel):
    location: Optional[Location]
    today: Weather
    forecast: Weather


@router.get('/weather', response_model=WeatherResponse)
async def weather():
    response = WeatherResponse(
        today=Weather(
            date_time=datetime.datetime.now(),
            temp_high=72,
            temp_low=50,
            humidity=60
        ),
        forecast=Weather(
            temp_high=75,
            temp_low=52,
            humidity=65
        )
    )
    return response


@router.get('/location', response_model=Location)
async def location() -> dict:
    response = Location(
        latitude=47.5733899,
        longitude=-122.1475309,
        city='Bellevue',
        county='King Country',
        country='USA',
        facts=[
            Fact(
                text='Dom lives close'
            ),
            Fact(
                text='T-Mobile is here'
            ),
        ]
    )
    return response