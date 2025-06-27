[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/datamindedacademy/skill-boost-consuming-apis)
# Skill Boost: Consuming APIs

This repository contains the exercises for the Skill Boost session on consuming APIs. It contains the code for running and deploying a simple FastAPI application that exposes two endpoints:

`/measurements/page`: a paginated endpoint that returns a list of measurements.

`/measurements/very-reliable`: an endpoint that, despite its name, is not very reliable and returns sometimes a 500 error.

For a full description of the endpoints and the query parameters, there is an OpenAPI specification available at `/docs`. You can run the API either locally via `make run-api`, or deploy it in the Dataminded Playground AWS account by applying the Terraform configuration in the `infra` directory. This will create an ECS service that is available at `skillboost.playground.dataminded.cloud`.

## Exercises

There are two exercises you can complete:

1. Make the `tests/test_very_reliable.py` test pass. It uses the `ingest_measurements` function from `main_sync.py` to fetch measurements from the `/measurements/very-reliable` endpoint. The test is currently failing because the endpoint is not very reliable and returns sometimes a 500 error. You can modify the `ingest_measurements` function to handle these errors. Tip: some [tenacity](https://tenacity.readthedocs.io/en/latest/) can help!
2. Implement the `ingest_measurements` functions in `main_async_measurements.py` and `main_multithreaded_measurements.py` using the `asyncio` and `multithreading` libraries, respectively. Then run the benchmark tests with `make benchmark` to see which implementation is faster. Can you explain the results?
