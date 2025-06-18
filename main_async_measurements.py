#!/usr/bin/env python3
"""
Device Measurements API Ingestion Script (Asynchronous)

This script fetches device measurements from the local API and saves them to a CSV file.
It uses asyncio and aiohttp for asynchronous HTTP requests.
"""

import asyncio
import csv
from datetime import datetime

import aiohttp

# API base URL and endpoint
BASE_URL = "http://localhost:8000"
MEASUREMENTS_ENDPOINT = "/measurements/page"


async def fetch_measurements(session, page=1, size=10, total=100, device_id=None):
    """
    Fetch measurements from the API using asynchronous requests.

    Args:
        session: aiohttp ClientSession
        page: Page number to fetch
        size: Number of items per page
        total: Total number of measurements to generate
        device_id: Filter by device ID

    Returns:
        JSON response from the API
    """
    # Prepare parameters
    params = {"page": page, "size": size, "total": total}

    if device_id:
        params["device_id"] = device_id

    url = f"{BASE_URL}{MEASUREMENTS_ENDPOINT}"

    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error: {response.status} - {await response.text()}")
                return None
    except Exception as e:
        print(f"Exception during API request: {e}")
        return None


async def save_to_csv(measurements, filename=None):
    """
    Save measurements to a CSV file.

    Args:
        measurements: List of measurement objects from the API
        filename: Name of the CSV file to save to

    Returns:
        Filename of the saved CSV file
    """
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"device_measurements_async_{timestamp}.csv"

    if not measurements:
        print("No measurements to save.")
        # Create an empty file
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["No measurements available"])
        print(f"Created empty file: {filename}")
        return filename

    # Define CSV fields based on the measurement object structure
    fields = [
        "id",
        "device_id",
        "timestamp",
        "temperature",
        "humidity",
        "pressure",
        "battery_level",
    ]

    print(f"Saving {len(measurements)} measurements to {filename}...")

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()

        for measurement in measurements:
            writer.writerow(measurement)

    print(f"Successfully saved to {filename}")
    return filename


async def ingest_measurements_async(
    max_pages=5, page_size=10, total=100, device_id=None
):
    """
    Ingest measurements from the API and save them to a CSV file using asyncio.

    This implementation creates separate tasks for each page and runs them concurrently.

    Args:
        max_pages: Maximum number of pages to fetch
        page_size: Number of items per page
        total: Total number of measurements to generate
        device_id: Filter by device ID

    Returns:
        Filename of the saved CSV file
    """
    all_measurements = []

    # Create timestamp for the CSV filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"device_measurements_async_{timestamp}.csv"

    async with aiohttp.ClientSession() as session:
        # Create a task for each page
        tasks = []
        for page in range(1, max_pages + 1):
            print(f"Creating task for page {page}...")
            task = asyncio.create_task(
                fetch_measurements(
                    session, page=page, size=page_size, total=total, device_id=device_id
                )
            )
            tasks.append(task)

        # Wait for all tasks to complete
        print(f"Waiting for {len(tasks)} tasks to complete...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process the results
        for i, result in enumerate(results):
            page_num = i + 1

            # Check if the result is an exception
            if isinstance(result, Exception):
                print(f"Error fetching page {page_num}: {result}")
                continue

            # Check if the result is None (request failed)
            if not result:
                print(f"Failed to fetch page {page_num}.")
                continue

            # Extract measurements from the response
            measurements = result.get("items", [])
            all_measurements.extend(measurements)

            print(f"Fetched {len(measurements)} measurements from page {page_num}")

    # Save all measurements to CSV
    print(f"Total measurements fetched: {len(all_measurements)}")
    return await save_to_csv(all_measurements, filename)


def ingest_measurements(max_pages=5, page_size=10, total=100, device_id=None):
    """
    Wrapper function to run the async function from synchronous code.

    Args:
        max_pages: Maximum number of pages to fetch
        page_size: Number of items per page
        total: Total number of measurements to generate
        device_id: Filter by device ID

    Returns:
        Filename of the saved CSV file
    """
    return asyncio.run(
        ingest_measurements_async(
            max_pages=max_pages, page_size=page_size, total=total, device_id=device_id
        )
    )


def main():
    """
    Main function to run the script.
    """
    print("Starting Device Measurements API ingestion (async)...")

    # Example usage: fetch measurements
    filename = ingest_measurements(max_pages=3, page_size=10, total=100)

    print(f"Completed! Data saved to {filename}")


if __name__ == "__main__":
    main()
