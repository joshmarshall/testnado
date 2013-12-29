Testnado - Test helpers for Tornado
===================================
This is a collection of several testing helpers I've compiled for Tornado, including authenticated fetch()ing and running Selenium sessions locally against Tornado applications.

Installation:
-------------
Install with:

    pip install testnado


... or if you are running bleeding edge, just:

    pip install ./

... from the downloaded / cloned directory.

Usage:
------
Most usage is as simple as, inside your tests, subclassing from HandlerTestCase instead of AsyncHTTPTestCase.

    from testnado import HandlerTestCase
    from testnado.credentials import HeaderCredentials
    from tornado.web import Application

    class MyHandlerTestCase(HandlerTestCase):

        def setUp(self):
            super(MyHandlerTestCase, self).setUp()
            # create your dummy user, however you want.
            self._user = User.create(...)

        def tearDown(self):
            super(MyHandlerTestCase, self).tearDown()
            # clean up your database, or whatever you used.
            self._user.delete_forever_haha()

        def get_app(self):
            return Application(["/", MyIndexHandler])

        def get_credentials(self):
            # return a credentials object that updates a
            # response object with the proper stuff
            return HeaderCredentials(token=self._user.token)


`testnado.HandlerTestCase` is a simple facade in front of composing more complicated test case behavior, like:

    from tornado.testing import AsyncHTTPTestCase
    from testnado import AuthenticatedFetchCase

    class MyHandlerTestCase(AsyncHTTPTestCase, AuthenticatedFetchCase):
        ...

This is obviously most helpful as a shared base class for all your Handler test cases, so writing tests is simpler:

    from mytests.helpers import MyHandlerTestCase

    class TestAwesomeAuthorization(MyHandlerTestCase):

        def test_auth(self):
            response = self.authenticated_fetch("/secret_resource")
            self.assertEqual(200, response.code)

        def test_auth_response(self):
            resource = Resource.create(user=self._user)
            response = self.authenticated_fetch("/" + resource.id)
            self.assertEqual(resource.view(), json.loads(response.body))


Credentials
-----------
Ultimately, `get_credentials()` should just return a callable. It will receive one argument of `fetch_arguments`, which is a named tuple. This should be updated in place. For instance:

    def get_credentials(self):
        def callback(fetch_arguments):
            fetch_arguments.headers.setdefault("Cookie", "token=FOOBAR")
            fetch_arguments.auth_username = "foo@bar.com"
            fetch_arguments.auth_password = "foobar"
            fetch_arguments.auth_mode = "basic"
        return callback

Of course, that's annoying, especially for more boilerplate-y use cases like secure cookies and safe header overwriting. For that reason, I've provided a few functor helpers (like HeaderCredentials above).

    from testnado.credentials import CookieCredentials

    # in the test case...

    def get_app(self):
        return Application(..., cookie_secret="foobar")

    def get_credentials(self):
        return CookieCredentials("auth", "token", cookie_secret="foobar")

Much shorter. I'll probably add a BasicAuthCredentials, but c'mon, how lazy are we. :)

Browser Testing
---------------
The automated browser testing requires PhantomJS (eventually other Selenium drivers) and bashes Selenium tests with the Golden Hammer of with contexts. It spins up a Tornado session in a thread, and gives a wrapped Selenium driver with helpers so you don't have to pass in full hosts / ports / credentials every test. This is mostly intended for full workflows, testing Javascript in-situ with Python, etc.

NOTE: Currently, we reuse a browser session for the entire life of nosetests. This is to keep tests from being annoyingly slow, but there are obvious pollution issues like history, localStorage, etc. We do clear all cookies after each with statement, though.

    from testnado import wrap_browser_session

    class SessionTestCase(HandlerTestCase):

        @wrap_browser_session()
        def test_index(self, driver):
            driver.get("/")
            driver.find_element_by_id("email").keys("foo@bar.com")
            driver.find_element_by_id("password").keys("foobar")
            driver.find_element_by_id("submit").click()
            self.assertTrue(driver.current_url.endswith("/dashboard"))
            # etc...

        @wrap_browser_session()
        def test_dashboard(self, driver):
            # uses get_credentials() from AuthenticatedFetchCase
            driver.authenticated_get("/dashboard")
            self.assertEqual(
                "Foo Bar",
                driver.find_element_by_id("name").text())

To Do
-----
I want to run tests as something other than PhantomJS. I would also like to use remote web drivers. Also, lots and lots of other little things to move over from my various projects.
