import collections


_FetchArguments = collections.namedtuple(
    "FetchArguments", [
        "url", "headers", "body", "auth_mode",
        "auth_password", "auth_username"
    ])


def build_fetch_arguments(url, **kwargs):
    kwargs["headers"] = kwargs.get("headers") or {}
    kwargs.setdefault("body", None)
    kwargs.setdefault("auth_mode", None)
    kwargs.setdefault("auth_password", None)
    kwargs.setdefault("auth_username", None)
    return _FetchArguments(url=url, **kwargs)
