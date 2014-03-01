import random
from testnado.browser_session import BrowserSession, IOLoopException
from testnado.browser_session import wrap_browser_session
from testnado.credentials.cookie_credentials import CookieCredentials
import time
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, asynchronous
from tornado.httpserver import HTTPServer
import unittest


_PORTS = range(18000, 18100)


def pop_port():
    port = random.choice(_PORTS)
    _PORTS.remove(port)
    return port


class IndexHandler(RequestHandler):

    def get(self):
        self.add_header("Content-type", "text/html")
        self.finish(
            "<html><head><title>Foo</title></head><body></body></html>")


class TimeoutHandler(RequestHandler):

    @asynchronous
    def get(self):
        self.application.settings["ioloop"].add_timeout(
            time.time() + 5, self._on_timeout)

    def _on_timeout(self):
        self.finish("<html><head><title>Foo</title></head></html>")


class AuthHandler(RequestHandler):

    def get(self, *args, **kwargs):
        title = "Forbidden"
        if self.get_secure_cookie("token") == "FOOBAR":
            title = "Allowed"
        self.finish(
            "<html>head><title>{}</title></head></html>".format(title))


class TestBrowserSession(unittest.TestCase):

    def setUp(self):
        super(TestBrowserSession, self).setUp()
        self._ioloop = IOLoop()
        self._app = Application([
            ("/", IndexHandler),
            ("/timeout", TimeoutHandler),
            ("/auth", AuthHandler)
        ], ioloop=self._ioloop, cookie_secret="foobar")
        self._server = HTTPServer(self._app, io_loop=self._ioloop)
        self._port = pop_port()

    def test_browser_session(self):
        self._server.listen(self._port)
        session = BrowserSession("phantomjs", ioloop=self._ioloop)
        with session as driver:
            driver.get("http://localhost:{}".format(self._port))
            self.assertEqual("Foo", driver.title)

    def test_browser_session_timeout(self):
        self._server.listen(self._port)
        session = BrowserSession("phantomjs", ioloop=self._ioloop, timeout=0.5)
        start_time = 0
        with self.assertRaises(IOLoopException):
            with session as driver:
                start_time = time.time()
                driver.get("http://localhost:{}/timeout".format(self._port))
        run_time = int(time.time() - start_time)
        self.assertTrue(
            run_time < 1, "IOLoop timeout took too long (%s)" % (run_time))

    def test_browser_session_decorator(self):
        ioloop = IOLoop()

        class DummyTest(object):

            io_loop = ioloop

            def get_app(test_case):
                return Application([("/", IndexHandler)])

            def get_http_port(test_case):
                return pop_port()

            @wrap_browser_session()
            def wrapped(test_case, driver):
                driver.get("/")
                self.assertEqual("Foo", driver.title)

        case = DummyTest()
        case.wrapped()

    def test_browser_session_authenticated(self):
        self._server.listen(self._port)
        session = BrowserSession("phantomjs", ioloop=self._ioloop)

        with session as driver:
            driver.get("http://localhost:{}/auth".format(self._port))
            self.assertEqual("Forbidden", driver.title)

        session = BrowserSession("phantomjs", ioloop=self._ioloop)
        credentials = CookieCredentials("token", "FOOBAR", "foobar")
        session.use_credentials(credentials)
        with session as driver:
            driver.get("http://localhost:{}/auth".format(self._port))
            self.assertEqual("Allowed", driver.title)

    def test_browser_session_decorator_with_credentials(self):
        ioloop = IOLoop()
        port = pop_port()

        class DummyTest(object):

            io_loop = ioloop

            def get_app(test_case):
                return Application([
                    ("/", IndexHandler),
                    ("/auth", AuthHandler)
                ], cookie_secret="foobar")

            def get_http_port(test_case):
                return port

            def get_credentials(test_case):
                return CookieCredentials("token", "FOOBAR", "foobar")

            @wrap_browser_session()
            def wrapped_auth(test_case, driver):
                driver.get("/auth")
                self.assertEqual("Allowed", driver.title)

            @wrap_browser_session(discover_credentials=False)
            def wrapped_noauth(test_case, driver):
                driver.get("/auth")
                self.assertEqual("Forbidden", driver.title)

        case = DummyTest()
        case.wrapped_auth()
        port = pop_port()
        case.wrapped_noauth()
