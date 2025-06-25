from skill_boost_consuming_apis.main_async_measurements import (
    ingest_measurements as ingest_measurements_async,
)
from skill_boost_consuming_apis.main_multithreaded_measurements import (
    ingest_measurements as ingest_measurements_threaded,
)
from skill_boost_consuming_apis.main_sync import (
    ingest_measurements as ingest_measurements_sync,
)

# Reduce the number of iterations for faster benchmarking
ITERATIONS = 1
ROUNDS = 1

# Test parameters
MAX_PAGES = 100
PAGE_SIZE = 10
TOTAL = 1000


def test_ingest_measurements_sync(benchmark):
    """Benchmark the synchronous ingest_measurements function."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_sync,
        kwargs={
            "endpoint": "/measurements/page",
            "max_pages": MAX_PAGES,
            "page_size": PAGE_SIZE,
            "total": TOTAL,
        },
        iterations=ITERATIONS,
        rounds=ROUNDS,
    )

    # Verify the result
    assert result is not None


def test_ingest_measurements_async(benchmark):
    """Benchmark the asynchronous ingest_measurements function."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_async,
        kwargs={
            "endpoint": "/measurements/page",
            "max_pages": MAX_PAGES,
            "page_size": PAGE_SIZE,
            "total": TOTAL,
        },
        iterations=ITERATIONS,
        rounds=ROUNDS,
    )

    assert result is not None


def test_ingest_measurements_threaded(benchmark):
    """Benchmark the multithreaded ingest_measurements function."""
    # Run the benchmark
    result = benchmark.pedantic(
        ingest_measurements_threaded,
        kwargs={
            "endpoint": "/measurements/page",
            "max_pages": MAX_PAGES,
            "page_size": PAGE_SIZE,
            "total": TOTAL,
        },
        iterations=ITERATIONS,
        rounds=ROUNDS,
    )

    # Verify the result
    assert result is not None
