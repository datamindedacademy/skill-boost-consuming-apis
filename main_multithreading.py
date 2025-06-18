import requests
from tenacity import (
    Retrying,
    before_sleep_log,
    stop_after_attempt,
    RetryCallState,
    retry_if_result,
)


from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sys

logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(threadName)s: %(message)s [%(filename)s:%(lineno)d in function %(funcName)s]",
    stream=sys.stderr,
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)

API_URL = "https://api.stackexchange.com"
API_VERSION = 2.3
MAX_WORKERS = 5
DEFAULT_TIMEOUT = 30


def get_url(endpoint: str) -> str:
    return f"{API_URL}/{API_VERSION}/{endpoint}"


def custom_wait(retry_state: RetryCallState):
    result = retry_state.outcome.result()
    if "backoff" in result:
        return result["backoff"]
    return 0  # default wait if not specified


def should_backoff(result):
    return "backoff" in result


def call(
    session: requests.Session,
    url: str,
    params: dict,
    timeout: int = DEFAULT_TIMEOUT,
    max_retries=3,
) -> dict:
    """
    Makes an api call handling known errors. In case of an known error, common approach is to wait a moment (e.g. server unavailable).
    During the waiting period, a hook function can be called to use idle time more efficiently (e.g. write intermediate results to db)
    """
    retryer = Retrying(
        retry=retry_if_result(should_backoff),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        wait=custom_wait,
        stop=stop_after_attempt(max_retries),
    )
    for attempt in retryer:
        with attempt:
            # Not using a context manager on a response object, results in a memory leak
            with session.get(
                url=url,
                params=params,
                timeout=timeout,
            ) as response:

                if response.status_code in (200, 201):
                    return response.json()

                response.raise_for_status()


def fetch_all_single_url(url: str, params: dict, session: requests.Session):
    results = []
    has_more = True

    if "page" not in params:
        params["page"] = 1

    while has_more:
        result = call(url=url, params=params, session=session)
        results.extend(result.get("items"))

        if params["page"] >= 5:
            break

        params["page"] += 1
        has_more = result["has_more"]

    return results


def fetch_multiple_urls(list_of_urls: list[str]):
    results = []
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(
                    fetch_all_single_url,
                    url,
                    params={"page": 1, "pagesize": 100, "site": "stackoverflow"},
                    session=session,
                ): url
                for url in list_of_urls
            }

        for future in as_completed(futures):
            results += future.result()
            # This ensures that the memory associated with the future is cleared after completion.
            futures.pop(future)

    return results


def main():
    params = {"pagesize": 100, "site": "stackoverflow"}

    answer_results = fetch_all_single_url(
        url=get_url("answers"), params=params, session=requests.Session()
    )

    list_of_urls = [
        get_url(f"answers/{result.get('answer_id')}/questions")
        for result in answer_results
    ]

    question_results = fetch_multiple_urls(list_of_urls=list_of_urls)

    print(question_results)


if __name__ == "__main__":
    main()
