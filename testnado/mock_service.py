import collections
import re

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from tornado.httpserver import HTTPServer
from tornado.testing import bind_unused_port
from tornado.web import Application, HTTPError, RequestHandler


try:
    basestring
except NameError:
    basestring = str


class MockService(object):

    def __init__(self, ioloop, port=None):
        self.ioloop = ioloop
        if port is None:
            self.socket, self.port = bind_unused_port()
        elif isinstance(port, tuple):
            self.socket, self.port = port
        else:
            self.socket, self.port = None, port
        self.host = "localhost:{0}".format(self.port)
        self.protocol = "http"
        self.base_url = "http://" + self.host
        self.routes = {}
        self._listening = False
        self._service = None

    def url(self, path):
        return urlparse.urljoin(self.base_url, path)

    def listen(self):
        # this is a bit annoying for the end user, but it's better than
        # "magically" starting the service, potentially before the user
        # has finished populating routes (or alternatively never starting)

        if not self.routes.items():
            # making a 'catchall', since without routes Tornado infinitely
            # redirects. this is only really useful for mocking without
            # testing responses (which is sketchy anyway...)
            handler = self.add_method("GET", "/(.*)", _unimplemented)
            handler.add_method("POST", _unimplemented)
            handler.add_method("PUT", _unimplemented)
            handler.add_method("OPTIONS", _unimplemented)
            handler.add_method("INFO", _unimplemented)

        application = Application(self.routes.items())
        if self.socket is not None:
            self._service = HTTPServer(application)
            self._service.add_socket(self.socket)
        else:
            self._service = application.listen(self.port)
        self._listening = True

    def stop(self):
        if self._service is not None:
            self._service.stop()

    def add_method(self, method, route, method_handler):
        # this only works with text (not regex) routes, but it's a helper
        # anyway so deal with it. :)
        handler = self.routes.setdefault(route, build_handler(route))
        handler.add_method(method, method_handler)
        return handler

    def assert_requested(self, method, path, headers=None):
        headers = headers or {}
        for handler in self.routes.values():
            if handler.route.match(path):
                try:
                    return handler.assert_requested(method, path, headers)
                except AssertionError:
                    continue
        raise AssertionError("No request matched: {} {}".format(method, path))

    def assert_not_requested(self, method, path, headers=None):
        try:
            self.assert_requested(method=method, path=path, headers=headers)
        except AssertionError:
            pass
        else:
            raise AssertionError(
                "Request was made to: {} {}".format(method, path))


class MockServiceMethods():

    def get(self, *args, **kwargs):
        return self._handle_method("GET", args, kwargs)

    def head(self, *args, **kwargs):
        return self._handle_method("HEAD", args, kwargs)

    def put(self, *args, **kwargs):
        return self._handle_method("PUT", args, kwargs)

    def patch(self, *args, **kwargs):
        return self._handle_method("PATCH", args, kwargs)

    def post(self, *args, **kwargs):
        return self._handle_method("POST", args, kwargs)

    def delete(self, *args, **kwargs):
        return self._handle_method("DELETE", args, kwargs)

    def options(self, *args, **kwargs):
        return self._handle_method("OPTIONS", args, kwargs)

    def info(self, *args, **kwargs):
        return self._handle_method("INFO", args, kwargs)

    def _handle_method(self, method, args, kwargs):
        self.requests.append(self.request)
        if method not in self.method_handlers:
            raise HTTPError(405, "Method '{}' has no handler.".format(method))
        return self.method_handlers[method](self, *args, **kwargs)

    @classmethod
    def add_method(cls, method, handler):
        cls.method_handlers[method.upper()] = handler
        if method not in cls.SUPPORTED_METHODS:
            cls.SUPPORTED_METHODS = cls.SUPPORTED_METHODS + (method,)

            def _custom_method(h, *args, **kwargs):
                return h._handle_method(method, args, kwargs)

            setattr(cls, method.lower(), _custom_method)

    @classmethod
    def assert_requested(cls, method, path, headers):
        for request in cls.requests:
            if not request.method == method:
                continue
            if not request.path == path:
                continue
            if not compare_dicts(
                    headers, request.headers, case_insensitive=True):
                continue

            if request.method == method and request.path == path:
                return request
        raise AssertionError("No request matched: {}".format(method))


def build_handler(handler_route):

    if isinstance(handler_route, basestring):
        handler_route = re.compile(handler_route)

    class Handler(MockServiceMethods, RequestHandler):
        route = handler_route
        requests = []
        method_handlers = {}

    return Handler


_Request = collections.namedtuple("Request", ["method", "path", "headers"])


def _unimplemented(handler, route):
    handler.set_status(501)
    handler.finish("UNIMPLEMENTED RESPONSE")


def compare_dicts(expected, actual, case_insensitive=False):
    if case_insensitive:
        expected = [(k.lower(), v) for k, v in expected.items()]
        actual = [(k.lower(), v) for k, v in actual.items()]
    return set(expected).issubset(actual)
