# Device Measurements API

A simple FastAPI application that provides an endpoint for generating random device measurement data.

## Features

- Generate random device measurement data points
- Filter by device ID
- Control the number of data points returned
- Multiple pagination options:
  - Page-based pagination (with optional navigation links)
  - Cursor-based pagination for efficient scrolling through large datasets

## Installation

1. Make sure you have Python 3.13+ installed
2. Install dependencies:

```bash
pip install -e .
```

## Running the API

Start the API server:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### GET /measurements (Deprecated)

Returns a list of random device measurement data points without pagination.

Query Parameters:
- `count` (optional): Number of measurements to generate (1-100, default: 5)
- `device_id` (optional): Filter by device ID

Example:
```
GET /measurements?count=10&device_id=device_1
```

### GET /measurements/page

Returns paginated random device measurement data using page-based pagination.

Query Parameters:
- `total` (optional): Total number of measurements to generate (1-1000, default: 100)
- `device_id` (optional): Filter by device ID
- `page` (optional): Page number (default: 1)
- `size` (optional): Items per page (default: 50)

Example:
```
GET /measurements/page?page=2&size=20&device_id=device_1
```

Response:
```json
{
  "items": [
    {
      "id": "uuid",
      "device_id": "device_1",
      "timestamp": "2023-06-18T10:30:00",
      "temperature": 24.5,
      "humidity": 65.2,
      "pressure": 1013.25,
      "battery_level": 78.5
    },
    ...
  ],
  "page": 2,
  "size": 20,
  "total": 100
}
```

### GET /measurements/page-with-links

Similar to `/measurements/page` but includes navigation links in the response.

Example:
```
GET /measurements/page-with-links?page=2&size=20
```

Response:
```json
{
  "items": [...],
  "page": 2,
  "size": 20,
  "total": 100,
  "links": {
    "first": "/measurements/page-with-links?page=1&size=20",
    "prev": "/measurements/page-with-links?page=1&size=20",
    "next": "/measurements/page-with-links?page=3&size=20",
    "last": "/measurements/page-with-links?page=5&size=20"
  }
}
```

### GET /measurements/cursor

Returns paginated random device measurement data using cursor-based pagination.

Query Parameters:
- `total` (optional): Total number of measurements to generate (1-1000, default: 100)
- `device_id` (optional): Filter by device ID
- `size` (optional): Items per page (default: 50)
- `after` (optional): Cursor for fetching the next page

Example:
```
GET /measurements/cursor?size=20
```

First page response:
```json
{
  "items": [...],
  "size": 20,
  "after": null,
  "next": "some-cursor-value"
}
```

Next page:
```
GET /measurements/cursor?size=20&after=some-cursor-value
```

## Data Model

Each measurement includes:
- `id`: Unique identifier for the measurement
- `device_id`: Identifier of the device
- `timestamp`: Time when the measurement was taken
- `temperature`: Temperature in Celsius
- `humidity`: Humidity percentage
- `pressure`: Atmospheric pressure in hPa
- `battery_level`: Device battery level percentage
