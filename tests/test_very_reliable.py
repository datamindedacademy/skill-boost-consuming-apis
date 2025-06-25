from skill_boost_consuming_apis.main_sync import ingest_measurements as ingest_measurements_very_reliable

# Define the very-reliable endpoint
VERY_RELIABLE_ENDPOINT = "/measurements/very-reliable"
NORMAL_ENDPOINT = "/measurements/page"


def test_fetch_measurements_very_reliable():
    response = ingest_measurements_very_reliable(
        endpoint=VERY_RELIABLE_ENDPOINT, max_pages=10, page_size=100, total=1000
    )
    assert response is not None, (
        "Failed to fetch measurements from /measurements/very-reliable endpoint"
    )

def test_fetch_measurements():
    response = ingest_measurements_very_reliable(
        endpoint=NORMAL_ENDPOINT, max_pages=10, page_size=100, total=1000
    )
    assert response is not None, (
        "Failed to fetch measurements from /measurements/page endpoint"
    )