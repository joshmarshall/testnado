from testnado.browser_session import BrowserSession, IOLoopException
from testnado.browser_session import wrap_browser_session
import time
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, asynchronous
from tornado.httpserver import HTTPServer
import unittest


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


class TestBrowserSession(unittest.TestCase):

    def setUp(self):
        super(TestBrowserSession, self).setUp()
        self._ioloop = IOLoop()
        self._app = Application([
            ("/", IndexHandler),
            ("/timeout", TimeoutHandler)
        ], ioloop=self._ioloop)
        self._server = HTTPServer(self._app, io_loop=self._ioloop)

    def test_browser_session(self):
        self._server.listen(18018)
        session = BrowserSession("phantomjs", ioloop=self._ioloop)
        with session.start(timeout=5) as driver:
            driver.get("http://localhost:18018")
            self.assertEqual("Foo", driver.title)

    def test_browser_session_timeout(self):
        self._server.listen(18019)
        session = BrowserSession("phantomjs", ioloop=self._ioloop)
        start_time = 0
        with self.assertRaises(IOLoopException):
            with session.start(timeout=1) as driver:
                start_time = time.time()
                driver.get("http://localhost:18019/timeout")
        run_time = int(time.time() - start_time)
        self.assertEqual(
            run_time, 1, "IOLoop timeout took too long (%s)" % (run_time))

    def test_browser_session_decorator(self):
        ioloop = IOLoop()

        class DummyTest(object):

            io_loop = ioloop

            def get_app(test_case):
                return Application([("/", IndexHandler)])

            def get_http_port(test_case):
                return 18020

            @wrap_browser_session()
            def wrapped(test_case, driver):
                driver.get("/")
                self.assertEqual("Foo", driver.title)

        case = DummyTest()
        case.wrapped()
