#!/usr/bin/env python3
"""
Benchmark tests for the API ingestion implementations.

This test requires the API to be running locally on http://localhost:8000.
You can start the API with: make run-api

This test compares the performance of synchronous, asynchronous, and multithreaded implementations,
both with and without file writing.
"""

import os
import sys

import pytest

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_async_measurements import ingest_measurements as ingest_measurements_async
from main_multithreaded_measurements import (
    ingest_measurements as ingest_measurements_threaded,
)
from main_sync import ingest_measurements as ingest_measurements_sync

# Reduce the number of iterations for faster benchmarking
ITERATIONS = 1
ROUNDS = 1

# Test parameters
MAX_PAGES = 100
PAGE_SIZE = 10
TOTAL = 1000


def test_ingest_measurements_sync_with_file(benchmark):
    """Benchmark the synchronous ingest_measurements function with file writing."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_sync,
        kwargs={
            "max_pages": MAX_PAGES,
            "page_size": PAGE_SIZE,
            "total": TOTAL,
            "save_to_file": True,
        },
        iterations=ITERATIONS,
        rounds=ROUNDS,
    )

    # Verify the result
    assert result is not None


def test_ingest_measurements_sync_without_file(benchmark):
    """Benchmark the synchronous ingest_measurements function without file writing."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_sync,
        kwargs={
            "max_pages": MAX_PAGES,
            "page_size": PAGE_SIZE,
            "total": TOTAL,
            "save_to_file": False,
        },
        iterations=ITERATIONS,
        rounds=ROUNDS,
    )

    # Verify the result
    assert result is not None


def test_ingest_measurements_async_with_file(benchmark):
    """Benchmark the asynchronous ingest_measurements function with file writing."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_async,
        kwargs={
            "max_pages": MAX_PAGES,
            "page_size": PAGE_SIZE,
            "total": TOTAL,
            "save_to_file": True,
        },
        iterations=ITERATIONS,
        rounds=ROUNDS,
    )

    assert result is not None


def test_ingest_measurements_async_without_file(benchmark):
    """Benchmark the asynchronous ingest_measurements function without file writing."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_async,
        kwargs={
            "max_pages": MAX_PAGES,
            "page_size": PAGE_SIZE,
            "total": TOTAL,
            "save_to_file": False,
        },
        iterations=ITERATIONS,
        rounds=ROUNDS,
    )

    # Verify the result
    assert result is not None


def test_ingest_measurements_threaded_with_file(benchmark):
    """Benchmark the multithreaded ingest_measurements function with file writing."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_threaded,
        kwargs={
            "max_pages": MAX_PAGES,
            "page_size": PAGE_SIZE,
            "total": TOTAL,
            "save_to_file": True,
        },
        iterations=ITERATIONS,
        rounds=ROUNDS,
    )

    # Verify the result
    assert result is not None


def test_ingest_measurements_threaded_without_file(benchmark):
    """Benchmark the multithreaded ingest_measurements function without file writing."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_threaded,
        kwargs={
            "max_pages": MAX_PAGES,
            "page_size": PAGE_SIZE,
            "total": TOTAL,
            "save_to_file": False,
        },
        iterations=ITERATIONS,
        rounds=ROUNDS,
    )

    # Verify the result
    assert result is not None


if __name__ == "__main__":
    pytest.main(["-v", __file__])
