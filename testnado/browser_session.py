import Cookie
from functools import wraps
import os
import Queue
from selenium import webdriver
import time
import threading
from tornado.ioloop import PeriodicCallback
from testnado.credentials.helpers import build_fetch_arguments


def wrap_browser_session(discover_credentials=True, *drivers):
    # right now drivers is a "fake" option -- anything other than phantomjs
    # will raise an Exception.
    drivers = drivers or ["phantomjs"]

    def test_wrapper(test_method):
        @wraps(test_method)
        def test_runner(test_case, *args, **kwargs):
            port = test_case.get_http_port()
            ioloop = test_case.io_loop
            credentials = None
            if hasattr(test_case, "get_credentials") and discover_credentials:
                credentials = test_case.get_credentials()

            for driver_name in drivers:
                session = BrowserSession(driver_name, ioloop=ioloop)
                with session as driver:
                    wrapped_driver = _WrapDriver(
                        driver, host="localhost", port=port)
                    kwargs["driver"] = wrapped_driver
                    if credentials:
                        wrapped_driver.get("/")
                        wrapped_driver.use_credentials(credentials)
                    test_method(test_case, *args, **kwargs)
        return test_runner
    return test_wrapper


class BrowserSession(object):

    def __init__(self, driver_name, ioloop, timeout=5):
        self._driver = _DRIVERS[driver_name]()
        self._ioloop = ioloop
        self._out_queue = Queue.Queue()
        self._in_queue = Queue.Queue()
        self._timeout = timeout

        keyword_arguments = {
            "in_queue": self._in_queue,
            "out_queue": self._out_queue
        }
        self._thread = threading.Thread(
            target=self._on_start, kwargs=keyword_arguments)

    def start(self):
        self._driver.set_page_load_timeout(self._timeout)
        self._thread.start()
        return self._driver

    def stop(self):
        self._in_queue.put("stop")
        self._thread.join()
        self._driver.delete_all_cookies()
        if not self._out_queue.empty():
            message = self._out_queue.get()
            raise IOLoopException("Error from IOLoop thread: %s" % (message))

    def _on_start(self, in_queue, out_queue):
        self._start_time = time.time()
        self._periodic_callback = PeriodicCallback(
            self._on_cycle, 100, io_loop=self._ioloop)
        self._periodic_callback.start()
        self._ioloop.start()

    def _on_cycle(self):
        if not self._in_queue.empty():
            message = self._in_queue.get()
            self._on_stop()
            if message != "stop":
                self._out_queue.put("unknown message %s" % (message))

        if time.time() - self._start_time > self._timeout:
            self._ioloop.stop()
            self._out_queue.put("timeout")

    def _on_stop(self):
        self._periodic_callback.stop()
        self._ioloop.stop()

    def __enter__(self):
        return self.start()

    def __exit__(self, *args, **kwargs):
        self.stop()


class IOLoopException(Exception):
    pass


class UnknownExecutable(Exception):
    pass


def _find_executable(executable_name):
    # silly Python 2.x and no builtin which...
    for folder in os.environ["PATH"].split(os.pathsep):
        folder = folder.strip()
        path = os.path.abspath(
            os.path.expanduser(os.path.join(folder, executable_name)))
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    raise UnknownExecutable("Could not find %s in PATH." % (executable_name))


def _build_phantomjs():
    if "phantomjs" not in _DRIVER_CACHE:
        driver_path = _find_executable("phantomjs")
        _DRIVER_CACHE["phantomjs"] = webdriver.PhantomJS(
            executable_path=driver_path)
    return _DRIVER_CACHE["phantomjs"]


_DRIVER_CACHE = {}


_DRIVERS = {
    "phantomjs": _build_phantomjs
}


class _WrapDriver(object):

    def __init__(self, driver, host, port):
        self._host = host
        self._port = port
        self._driver = driver

    def get(self, path):
        full_url = "http://%s:%s%s" % (self._host, self._port, path)
        self._driver.get(full_url)

    def use_credentials(self, credentials):
        fetch_arguments = build_fetch_arguments("/")
        credentials(fetch_arguments)
        # Selenium doesn't support arbitrary headers (afaik), so we only
        # support cookies for now.
        if "Cookie" in fetch_arguments.headers:
            cookie = Cookie.SimpleCookie()
            cookie.load(fetch_arguments.headers["Cookie"])
            for morsel_name, morsel in cookie.items():
                self._driver.add_cookie({
                    "name": morsel_name,
                    "value": morsel.value
                })

    def __getattr__(self, attribute):
        return getattr(self._driver, attribute)
