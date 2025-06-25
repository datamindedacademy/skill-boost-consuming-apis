#!/usr/bin/env python3
"""
Device Measurements API Ingestion Script (Multithreaded)

This script fetches device measurements from the local API and saves them to a CSV file.
It uses the standard library's threading module for concurrent HTTP requests.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sys
from tenacity import (
    before_sleep_log,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
    retry
)

import requests

logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(threadName)s: %(message)s [%(filename)s:%(lineno)d in function %(funcName)s]",
    stream=sys.stderr,
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


# API base URL and endpoint
BASE_URL = "https://skillboost.playground.dataminded.cloud"
MEASUREMENTS_ENDPOINT = "/measurements/page"
RELIABLE_ENDPOINT = "measurements/very-reliable"
MAX_RETRIES = 5
MAX_WORKERS = 5

@retry(
    retry=retry_if_exception_type(requests.exceptions.HTTPError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    wait=wait_fixed(0.5),
    stop=stop_after_attempt(MAX_RETRIES),
)
def fetch_page(
    session: requests.Session,
    url,
    page=1,
    size=10,
    total=100,
):
    """
    Fetch measurements from the API using synchronous requests.

    Args:
        session: request.Session object for performance
        url: URL to execute GET request against
        page: Page number to fetch
        size: Number of items per page
        total: Total number of measurements to generate

    Returns:
        JSON response from the API
    """

    # Prepare parameters
    params = {"page": page, "size": size, "total": total}

    # Not using a context manager on a response object, results in a memory leak
    with session.get(
        url=url,
        params=params,
    ) as response:

        if response.status_code in (200, 201):
            return response.json()

        response.raise_for_status()




def ingest_endpoint(
    url: str = f"{BASE_URL}/{MEASUREMENTS_ENDPOINT}",
    endpoint:str = "measurements",
    max_pages=5,
    page_size=10,
    total=100,
):
    """
    Ingest measurements from the API using multithreading.

    Args:
        url: URL of the endpoint we want to consume
        endpoint: endpoint name for logging
        max_pages: Maximum number of pages to fetch
        page_size: Number of items per page
        total: Total number of measurements to generate

    Returns:
        List of measurements
    """
    all_results = []

    with requests.Session() as session:
        # Create and start threads for each page
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit tasks to the executor
            page_futures = {
                executor.submit(
                    fetch_page, session, url, page, page_size, total,
                ): page
                for page in range(1, max_pages + 1)
            }

        for future in as_completed(page_futures):
            response = future.result()
            # Make sure each future is cleared from memory
            page = page_futures.pop(future)

            # process api call result
            if not response:
                logger.info(f"No result for page {page}.")
                continue

            results = response.get("items", [])
            all_results.extend(results)
            logger.info(f"Processed {len(results)} measurements from page {page}")

            # Check if we've reached the last page
            if len(results) < page_size:
                logger.info("No more pages available.")
                break

    # Return all measurements
    logger.info(f"Total measurements fetched: {len(all_results)}")
    return all_results

def ingest_measurements(
    endpoint: str = MEASUREMENTS_ENDPOINT,
    max_pages=5,
    page_size=10,
    total=100):

    measurements_url=f"{BASE_URL}{endpoint}"

    logger.info("Starting Device Measurements API ingestion (multithreaded)...")

    measurements = ingest_endpoint(
        url=measurements_url,
        endpoint="measurements",
        max_pages=max_pages,
        page_size=page_size,
        total=total,
    )

    logger.info(f"Completed! Fetched {len(measurements)} measurements")

    return measurements

def ingest_measurements_reliable(
    endpoint: str = f"/{RELIABLE_ENDPOINT}",
    max_pages=5,
    page_size=10,
    total=100):

    measurements_url=f"{BASE_URL}{endpoint}"

    logger.info("Starting Device Measurements API ingestion (multithreaded)...")

    measurements = ingest_endpoint(
        url=measurements_url,
        endpoint="measurements",
        max_pages=max_pages,
        page_size=page_size,
        total=total,
    )

    logger.info(f"Completed! Fetched {len(measurements)} measurements")

    return measurements


def main():
    """
    Main function to run the script.
    """
    ingest_measurements_reliable(endpoint=f"/{RELIABLE_ENDPOINT}")


if __name__ == "__main__":
    main()
