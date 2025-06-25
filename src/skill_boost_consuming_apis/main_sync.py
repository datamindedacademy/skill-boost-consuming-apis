#!/usr/bin/env python3
"""
Device Measurements API Ingestion Script (Synchronous)

This script fetches device measurements from the local API and saves them to a CSV file.
It uses the requests library for synchronous HTTP requests.
"""

import requests

# API base URL and endpoint
BASE_URL = "https://skillboost.playground.dataminded.cloud"
MEASUREMENTS_ENDPOINT = "/measurements/page"


def fetch_measurements(endpoint: str, page=1, size=10, total=100):
    """
    Fetch measurements from the API using synchronous requests.

    Args:
        page: Page number to fetch
        size: Number of items per page
        total: Total number of measurements to generate
        device_id: Filter by device ID

    Returns:
        JSON response from the API
    """
    url = f"{BASE_URL}{endpoint}"

    response = requests.get(url, params={"page": page, "size": size, "total": total})
    if response.status_code == 200:
        return response.json()

    response.raise_for_status()


def ingest_measurements(
    endpoint: str,
    max_pages=5,
    page_size=10,
    total=100,
):
    """
    Ingest measurements from the API and optionally save them to a CSV file.

    Args:
        max_pages: Maximum number of pages to fetch
        page_size: Number of items per page
        total: Total number of measurements to generate
        device_id: Filter by device ID
        save_to_file: Whether to save the measurements to a CSV file

    Returns:
        Filename of the saved CSV file if save_to_file is True, otherwise the list of measurements
    """
    all_measurements = []

    for page in range(1, max_pages + 1):
        print(f"Fetching page {page}...")
        response = fetch_measurements(
            endpoint=endpoint,
            page=page,
            size=page_size,
            total=total,
        )

        if not response:
            print(f"Failed to fetch page {page}. Stopping.")
            break

        # Extract measurements from the response
        measurements = response.get("items", [])
        all_measurements.extend(measurements)

        print(f"Fetched {len(measurements)} measurements from page {page}")

        # Check if we've reached the last page
        if len(measurements) < page_size:
            print("No more pages available.")
            break

    return all_measurements


def main():
    """
    Main function to run the script.
    """
    print("Starting Device Measurements API ingestion...")

    # Example usage: fetch measurements
    filename = ingest_measurements(
        endpoint=MEASUREMENTS_ENDPOINT, max_pages=3, page_size=10, total=100
    )

    print(f"Completed! Data saved to {filename}")


if __name__ == "__main__":
    main()
