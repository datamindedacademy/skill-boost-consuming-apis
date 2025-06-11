#!/usr/bin/env python3
"""
Stack Exchange API Answers Ingestion Script

This script fetches answers from the Stack Exchange API and saves them to a CSV file.
It uses asyncio and aiohttp for asynchronous HTTP requests.
"""

import asyncio
import csv
import os
from datetime import datetime

import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
API_KEY = os.getenv("STACK_EXCHANGE_API_KEY")

# Stack Exchange API base URL and endpoint
BASE_URL = "https://api.stackexchange.com/2.3"
ANSWERS_ENDPOINT = "/answers"

# Default parameters for the API request
DEFAULT_PARAMS = {
    "site": "stackoverflow",  # Default site is Stack Overflow
    "pagesize": 100,  # Number of items per page
    "order": "desc",  # Descending order
    "sort": "activity",  # Sort by activity
    # "filter": "!-*f(6t0EUqUz",  # Filter to include body, comments, and other details
}


async def fetch_answers(session, page=1, **kwargs):
    """
    Fetch answers from the Stack Exchange API.

    Args:
        session: aiohttp ClientSession
        page: Page number to fetch
        **kwargs: Additional parameters to pass to the API

    Returns:
        JSON response from the API
    """
    # Combine default parameters with any additional parameters
    params = {**DEFAULT_PARAMS, **kwargs, "page": page}

    # Add API key if available
    if API_KEY:
        params["key"] = API_KEY

    url = f"{BASE_URL}{ANSWERS_ENDPOINT}"

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


async def save_to_csv(answers, filename=None):
    """
    Save answers to a CSV file.

    Args:
        answers: List of answer objects from the API
        filename: Name of the CSV file to save to
    """
    if not answers:
        print("No answers to save.")
        return

    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stack_exchange_answers_{timestamp}.csv"

    # Define CSV fields based on the answer object structure
    fields = [
        "answer_id",
        "question_id",
        "creation_date",
        "last_activity_date",
        "score",
        "is_accepted",
        "owner_user_id",
        "owner_display_name",
        "owner_reputation",
        "comment_count",
        "link",
    ]

    print(f"Saving {len(answers)} answers to {filename}...")

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()

        for answer in answers:
            # Extract owner information safely
            owner = answer.get("owner", {})

            # Create a row with the desired fields
            row = {
                "answer_id": answer.get("answer_id"),
                "question_id": answer.get("question_id"),
                "creation_date": datetime.fromtimestamp(
                    answer.get("creation_date", 0)
                ).isoformat()
                if answer.get("creation_date")
                else "",
                "last_activity_date": datetime.fromtimestamp(
                    answer.get("last_activity_date", 0)
                ).isoformat()
                if answer.get("last_activity_date")
                else "",
                "score": answer.get("score"),
                "is_accepted": answer.get("is_accepted", False),
                "owner_user_id": owner.get("user_id", ""),
                "owner_display_name": owner.get("display_name", ""),
                "owner_reputation": owner.get("reputation", ""),
                "comment_count": answer.get("comment_count", 0),
                "link": answer.get("link", ""),
            }

            writer.writerow(row)

    print(f"Successfully saved to {filename}")


async def main_async(
    tags=None, from_date=None, to_date=None, site="stackoverflow", max_pages=5
):
    """
    Main async function to fetch answers and save them to a CSV file.

    Args:
        tags: List of tags to filter answers by
        from_date: Start date for answers (Unix timestamp)
        to_date: End date for answers (Unix timestamp)
        site: Stack Exchange site to query
        max_pages: Maximum number of pages to fetch
    """
    # Prepare parameters
    params = {"site": site}

    if tags:
        params["tagged"] = ";".join(tags)

    if from_date:
        params["fromdate"] = from_date

    if to_date:
        params["todate"] = to_date

    all_answers = []

    # Create timestamp for the CSV filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stack_exchange_answers_{timestamp}.csv"

    async with aiohttp.ClientSession() as session:
        for page in range(1, max_pages + 1):
            print(f"Fetching page {page}...")
            response = await fetch_answers(session, page=page, **params)

            if not response:
                print(f"Failed to fetch page {page}. Stopping.")
                break

            answers = response.get("items", [])
            all_answers.extend(answers)

            print(f"Fetched {len(answers)} answers from page {page}")

            # Check if we've reached the last page
            if not response.get("has_more", False):
                print("No more pages available.")
                break

            # Respect API rate limits with a small delay
            await asyncio.sleep(0.1)

    # Save all answers to CSV
    await save_to_csv(all_answers, filename)

    return filename


def main():
    """
    Main function to run the script.
    """
    print("Starting Stack Exchange API answers ingestion...")

    # Example usage: fetch Python-related answers from the last month
    # You can modify these parameters or add command-line argument parsing
    tags = ["python"]

    # Run the async function
    filename = asyncio.run(main_async(tags=tags, max_pages=3))

    print(f"Completed! Data saved to {filename}")


if __name__ == "__main__":
    main()
