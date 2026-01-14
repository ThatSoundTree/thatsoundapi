import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception,
    retry_if_result,
)

RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


def is_retryable_response(response: httpx.Response) -> bool:
    return response.status_code in RETRYABLE_STATUS_CODES


def is_retryable_exception(exc: BaseException) -> bool:
    return isinstance(
        exc,
        (
            httpx.ConnectError,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
            httpx.RemoteProtocolError,
        ),
    )


retry_policy = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(
        initial=0.5,
        max=10.0,
    ),
    retry=(
        retry_if_exception(is_retryable_exception)
        | retry_if_result(is_retryable_response)
    ),
    reraise=True,
)
