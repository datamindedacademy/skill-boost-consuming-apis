#!/usr/bin/env python3
"""
Benchmark tests for the API ingestion implementations.

This test requires the API to be running locally on http://localhost:8000.
You can start the API with: make run-api

This test compares the performance of synchronous and asynchronous implementations.
"""

import os
import sys

import pytest

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_async_measurements import ingest_measurements as ingest_measurements_async
from main_sync import ingest_measurements as ingest_measurements_sync
from main_multithreaded_measurements import ingest_measurements as ingest_measurements_threaded

ITERATIONS = 100

def test_ingest_measurements_sync(benchmark):
    """Benchmark the synchronous ingest_measurements function."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_sync,
        kwargs={"max_pages": 3, "page_size": 10, "total": 100},
        iterations=ITERATIONS,
        rounds = 10,
    )

    # Verify the result
    assert result is not None
    assert result.endswith(".csv")

    # Clean up the file
    if os.path.exists(result):
        os.remove(result)


def test_ingest_measurements_async(benchmark):
    """Benchmark the asynchronous ingest_measurements function."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_async,
        kwargs={"max_pages": 3, "page_size": 10, "total": 100},
        iterations=ITERATIONS,
        rounds = 10,
    )

    # Verify the result
    assert result is not None
    assert result.endswith(".csv")

    # Clean up the file
    if os.path.exists(result):
        os.remove(result)


def test_ingest_measurements_threaded(benchmark):
    """Benchmark the multithreaded ingest_measurements function."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_threaded,
        kwargs={"max_pages": 3, "page_size": 10, "total": 100},
        iterations=ITERATIONS,
        rounds = 10,
    )

    # Verify the result
    assert result is not None
    assert result.endswith(".csv")

    # Clean up the file
    if os.path.exists(result):
        os.remove(result)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
