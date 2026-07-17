"""Unit tests for refresh.classify_exception — maps raised exceptions to one of
four failure classes that drive the retry policy."""
import json
import socket
import urllib.error

import pytest

from aifeeder.refresh import classify_exception


def test_url_error_is_transient() -> None:
    assert classify_exception(urllib.error.URLError("network down")) == "transient"


def test_socket_timeout_is_transient() -> None:
    assert classify_exception(socket.timeout()) == "transient"


def test_timeout_error_is_transient() -> None:
    assert classify_exception(TimeoutError()) == "transient"


def test_json_decode_error_is_content() -> None:
    err = json.JSONDecodeError("expecting value", "doc", 0)
    assert classify_exception(err) == "content"


def test_unknown_exception_falls_through_to_unknown() -> None:
    assert classify_exception(ValueError("something weird")) == "unknown"


def test_openai_errors_classified_when_sdk_available() -> None:
    """If the openai SDK is installed, RateLimitError + APIConnectionError +
    APITimeoutError should map to 'transient'; AuthenticationError to 'permanent'.
    Construction signatures for these errors vary across openai SDK versions,
    so we use isinstance checks on the *class* via type-spoofing rather than
    instantiating real errors (some need a real httpx.Response)."""
    pytest.importorskip("openai")
    import openai

    # Subclass each error type with a no-arg __init__ so we can instantiate
    # without faking httpx machinery, while keeping isinstance(...) True.
    class _RL(openai.RateLimitError):
        def __init__(self): pass
    class _Auth(openai.AuthenticationError):
        def __init__(self): pass

    assert classify_exception(_RL()) == "transient"
    assert classify_exception(_Auth()) == "permanent"
