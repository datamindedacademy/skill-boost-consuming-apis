#!/usr/bin/env python3
"""
Device Measurements API Ingestion Script (Asynchronous)

This script fetches device measurements from the local API and saves them to a CSV file.
It uses asyncio and aiohttp for asynchronous HTTP requests.
"""

import asyncio

import aiohttp

# API base URL and endpoint
BASE_URL = "https://skillboost.playground.dataminded.cloud"
MEASUREMENTS_ENDPOINT = "/measurements/page"


async def fetch_measurements(session, endpoint: str, page=1, size=10, total=100):
    """
    Fetch measurements from the API using asynchronous requests.

    Args:
        session: aiohttp ClientSession
        endpoint: API endpoint to fetch from
        page: Page number to fetch
        size: Number of items per page
        total: Total number of measurements to generate

    Returns:
        JSON response from the API
    """
    # Prepare parameters
    params = {"page": page, "size": size, "total": total}

    url = f"{BASE_URL}{endpoint}"

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




async def ingest_measurements_async(
    endpoint: str, max_pages=5, page_size=10, total=100
):
    """
    Ingest measurements from the API using asyncio.

    This implementation creates separate tasks for each page and runs them concurrently.

    Args:
        endpoint: API endpoint to fetch from
        max_pages: Maximum number of pages to fetch
        page_size: Number of items per page
        total: Total number of measurements to generate

    Returns:
        List of measurements
    """
    all_measurements = []

    async with aiohttp.ClientSession() as session:
        # Create a task for each page
        tasks = []
        for page in range(1, max_pages + 1):
            print(f"Creating task for page {page}...")
            task = asyncio.create_task(
                fetch_measurements(
                    session, endpoint=endpoint, page=page, size=page_size, total=total
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

    # Return all measurements
    print(f"Total measurements fetched: {len(all_measurements)}")
    return all_measurements


def ingest_measurements(
    endpoint: str = MEASUREMENTS_ENDPOINT, max_pages=5, page_size=10, total=100
):
    """
    Wrapper function to run the async function from synchronous code.

    Args:
        endpoint: API endpoint to fetch from
        max_pages: Maximum number of pages to fetch
        page_size: Number of items per page
        total: Total number of measurements to generate

    Returns:
        List of measurements
    """
    return asyncio.run(
        ingest_measurements_async(
            endpoint=endpoint,
            max_pages=max_pages,
            page_size=page_size,
            total=total,
        )
    )


def main():
    """
    Main function to run the script.
    """
    print("Starting Device Measurements API ingestion (async)...")

    # Example usage: fetch measurements
    measurements = ingest_measurements(endpoint=MEASUREMENTS_ENDPOINT, max_pages=3, page_size=10, total=100)

    print(f"Completed! Fetched {len(measurements)} measurements")


if __name__ == "__main__":
    main()
