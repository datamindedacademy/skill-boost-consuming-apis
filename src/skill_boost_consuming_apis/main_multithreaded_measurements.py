#!/usr/bin/env python3
"""
Device Measurements API Ingestion Script (Multithreaded)

This script fetches device measurements from the local API and saves them to a CSV file.
It uses the standard library's threading module for concurrent HTTP requests.
"""

import logging
import sys

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


def ingest_measurements(
    endpoint: str = f"/{RELIABLE_ENDPOINT}", max_pages=5, page_size=10, total=100
):
    pass


def main():
    """
    Main function to run the script.
    """
    ingest_measurements(endpoint=f"/{RELIABLE_ENDPOINT}")


if __name__ == "__main__":
    main()
