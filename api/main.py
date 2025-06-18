import random
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi_pagination import Page, add_pagination, paginate, set_page, set_params
from fastapi_pagination.default import Params
from pydantic import BaseModel

app = FastAPI(title="Device Measurements API")

# Add pagination to the FastAPI app
add_pagination(app)


class Measurement(BaseModel):
    id: str
    device_id: str
    timestamp: datetime
    temperature: float
    humidity: float
    pressure: float
    battery_level: float

    # For cursor-based pagination, we need a field to sort by
    def get_cursor_value(self) -> str:
        return self.id


@app.get("/")
async def root():
    return {"message": "Device Measurements API"}


def generate_measurements(
    count: int = 100, device_id: Optional[str] = None
) -> List[Measurement]:
    """Helper function to generate random measurements"""
    measurements = []

    random.seed(42)  # For reproducibility

    # Use provided device_id or generate random ones
    device_ids = [device_id] if device_id else [f"device_{i}" for i in range(1, 6)]

    for i in range(count):
        # Random device if no specific device_id was provided
        selected_device = device_id if device_id else random.choice(device_ids)

        # Random timestamp within the last 24 hours
        random_minutes = random.randint(0, 24 * 60)
        timestamp = datetime(year=2025, month=6, day=18) + random_minutes * timedelta(
            minutes=1
        )

        # Use a deterministic ID for cursor-based pagination to work properly
        measurement_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"measurement-{i}"))

        measurement = Measurement(
            id=measurement_id,
            device_id=selected_device,
            timestamp=timestamp,
            temperature=round(random.uniform(15.0, 35.0), 2),
            humidity=round(random.uniform(30.0, 90.0), 2),
            pressure=round(random.uniform(980.0, 1050.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
        )
        measurements.append(measurement)

    # Sort by timestamp (newest first)
    measurements.sort(key=lambda x: x.timestamp, reverse=True)

    return measurements


@app.get("/measurements", response_model=List[Measurement], deprecated=True)
async def get_measurements_legacy(
    count: int = Query(
        5, description="Number of measurements to generate", ge=1, le=100
    ),
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
):
    """
    Legacy endpoint without pagination (deprecated).
    Use /measurements/page or /measurements/cursor instead.
    """
    return generate_measurements(count, device_id)[:count]


@app.get("/measurements/page", response_model=Page[Measurement])
async def get_measurements_page(
    total: int = Query(
        100, description="Total number of measurements to generate", ge=1, le=1000
    ),
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    page: int = Query(1, description="Page number", ge=1),
    size: int = Query(10, description="Items per page", ge=1, le=100),
):
    """
    Get measurements with page-based pagination.

    Page-based pagination uses page number and size parameters.
    """
    # Generate the measurements
    measurements = generate_measurements(total, device_id)

    # Set up pagination parameters
    set_page(Page[Measurement])
    set_params(Params(page=page, size=size))

    # Apply pagination to the measurements
    return paginate(measurements)


@app.get("/measurements/very-reliable", response_model=Page[Measurement])
async def get_measurements_unreliable(
    total: int = Query(
        100, description="Total number of measurements to generate", ge=1, le=1000
    ),
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    page: int = Query(1, description="Page number", ge=1),
    size: int = Query(10, description="Items per page", ge=1, le=100),
):
    """
    Get measurements with page-based pagination and a 30% chance of server error.

    This endpoint simulates an unreliable API that occasionally fails with a 500 error.
    It uses page-based pagination like /measurements/page.
    """
    # Create a new random number generator that's not affected by the seed in generate_measurements
    unseeded_random = random.Random()

    # 10% chance of returning a server error using the unseeded random generator
    if unseeded_random.random() < 0.3:
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: contact support for more information.",
        )

    # Generate the measurements
    measurements = generate_measurements(total, device_id)
    
    # Set up pagination parameters
    set_page(Page[Measurement])
    set_params(Params(page=page, size=size))
    
    # Apply pagination to the measurements
    return paginate(measurements)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
