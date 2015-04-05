# This is used when a mock service can't be constructed, so we intercept
# the fetch. It's not as thorough, since the response object is not
# complete, the network behavior different, etc. but sometimes you
# just can't change internal fetching parameters for dependent libraries.

import contextlib
import mock

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.httputil import HTTPHeaders


class MockClient(object):

    def __init__(self, ioloop):
        self.ioloop = ioloop
        self.mocked_urls = {}
        self.client = AsyncHTTPClient(self.ioloop)
        self.original_fetch = self.client.fetch

    def mock_url(self, url):
        mock_response = MockResponse(url)
        base_url = url.split("?")[0]
        self.mocked_urls.setdefault(base_url, []).append(mock_response)
        return mock_response

    @contextlib.contextmanager
    def patch(self):
        # this is perhaps a bit sketchy -- basing on the idea that
        # AsyncHTTPClient returns the singleton...
        with mock.patch.object(self.client, "fetch", self.fetch):
            yield

    @gen.coroutine
    def fetch(self, url, *args, **kwargs):
        base_url = url.split("?")[0]

        if base_url not in self.mocked_urls:
            response = yield self.original_fetch(url, *args, **kwargs)
            raise gen.Return(response)

        responses = self.mocked_urls[base_url]

        if len(responses) == 0:
            raise MissingMockResponse(
                "URL requested too many times: {}".format(base_url))

        response = responses.pop(0)
        if response.code > 399 and kwargs.get("raise_error", True):
            raise HTTPError(
                code=response.code, message="Error requesting resource",
                response=response)
        raise gen.Return(response)


class MockResponse(object):

    def __init__(self, url):
        self.code = 200
        self._body = ""
        self._headers = HTTPHeaders()
        self._custom_headers = {}

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    @property
    def headers(self):
        self._headers.setdefault("Content-Length", len(self._body))
        return self._headers


class MissingMockResponse(Exception):
    pass
