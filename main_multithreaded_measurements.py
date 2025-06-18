#!/usr/bin/env python3
"""
Device Measurements API Ingestion Script (Multithreaded)

This script fetches device measurements from the local API and saves them to a CSV file.
It uses the standard library's threading module for concurrent HTTP requests.
"""

import csv
import queue
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

# API base URL and endpoint
BASE_URL = "http://localhost:8000"
MEASUREMENTS_ENDPOINT = "/measurements/page"


def fetch_measurements(page=1, size=10, total=100, device_id=None):
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
    # Prepare parameters
    params = {"page": page, "size": size, "total": total}

    if device_id:
        params["device_id"] = device_id

    url = f"{BASE_URL}{MEASUREMENTS_ENDPOINT}"

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception during API request: {e}")
        return None


def fetch_page_worker(page, size, total, device_id, result_queue):
    """
    Worker function to fetch a page of measurements and put the result in a queue.

    Args:
        page: Page number to fetch
        size: Number of items per page
        total: Total number of measurements to generate
        device_id: Filter by device ID
        result_queue: Queue to put the result in
    """
    print(f"Thread fetching page {page}...")
    response = fetch_measurements(
        page=page, size=size, total=total, device_id=device_id
    )

    # Put a tuple of (page_number, response) in the queue
    result_queue.put((page, response))


def save_to_csv(measurements, filename=None):
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
        filename = f"device_measurements_threaded_{timestamp}.csv"

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


def ingest_measurements(
    max_pages=5, page_size=10, total=100, device_id=None, save_to_file=True
):
    """
    Ingest measurements from the API and optionally save them to a CSV file using multithreading.

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

    # Create timestamp for the CSV filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"device_measurements_threaded_{timestamp}.csv"

    # Create a queue to store the results
    result_queue = queue.Queue()

    # Create and start threads for each page
    with ThreadPoolExecutor(max_workers=max_pages) as executor:
        # Submit tasks to the executor
        for page in range(1, max_pages + 1):
            executor.submit(
                fetch_page_worker, page, page_size, total, device_id, result_queue
            )

    # Process the results from the queue
    results = {}
    while not result_queue.empty():
        page, response = result_queue.get()
        results[page] = response

    # Process the results in order
    for page in range(1, max_pages + 1):
        response = results.get(page)

        if not response:
            print(f"No result for page {page}.")
            continue

        # Extract measurements from the response
        measurements = response.get("items", [])
        all_measurements.extend(measurements)

        print(f"Processed {len(measurements)} measurements from page {page}")

        # Check if we've reached the last page
        if len(measurements) < page_size:
            print("No more pages available.")
            break

    # Save all measurements to CSV if requested
    print(f"Total measurements fetched: {len(all_measurements)}")
    if save_to_file:
        return save_to_csv(all_measurements, filename)
    else:
        return all_measurements


def main():
    """
    Main function to run the script.
    """
    print("Starting Device Measurements API ingestion (multithreaded)...")

    # Example usage: fetch measurements
    filename = ingest_measurements(max_pages=3, page_size=10, total=100)

    print(f"Completed! Data saved to {filename}")


if __name__ == "__main__":
    main()
