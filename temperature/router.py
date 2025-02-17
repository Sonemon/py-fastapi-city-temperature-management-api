from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db
from . import crud, schemas
from city import crud as city_crud


router = APIRouter()
asyncSession = Depends(get_db)


@router.get("/temperatures/")
async def read_temperatures(db: AsyncSession = asyncSession):
    return await crud.get_all_temperatures(db=db)


@router.get("/temperatures/{city_id}/", response_model=list[schemas.Temperature])
async def read_temperatures_by_city(city_id: int, db: AsyncSession = asyncSession):
    temperatures = await crud.get_temperatures_by_city(db=db, city_id=city_id)
    if not temperatures:
        raise HTTPException(status_code=404, detail="No temperatures found for this city")
    return temperatures


@router.post("/temperatures/update/")
async def update_temperatures(db: AsyncSession = asyncSession):
    cities = await city_crud.get_all_cities(db=db)
    if not cities:
        raise HTTPException(status_code=404, detail="No cities found")

    for city in cities:
        try:
            temperature = await crud.fetch_temperature_by_city(city.name)
            await crud.create_update_temperature(db=db, city_id=city.id, temperature=temperature)
        except HTTPException as e:
            print(f"Failed to update temperature for {city.name}: {e.detail}")
        except Exception as e:
            print(f"Unexpected error for {city.name}: {str(e)}")

