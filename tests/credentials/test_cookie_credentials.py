try:
    from Cookie import SimpleCookie
except ImportError:
    from http.cookies import SimpleCookie

import unittest
from testnado.credentials.cookie_credentials import CookieCredentials
from testnado.credentials.helpers import build_fetch_arguments
from tornado.web import decode_signed_value


class TestCookieCredentials(unittest.TestCase):

    def test_cookie_credentials(self):
        fetch_arguments = build_fetch_arguments("/foobar")
        credentials = CookieCredentials(
            cookie_name="auth", cookie_value="token", cookie_secret="foobar")
        credentials(fetch_arguments)
        self.assertTrue("Cookie" in fetch_arguments.headers)

        cookie = SimpleCookie()
        cookie.load(fetch_arguments.headers["Cookie"])
        self.assertTrue("auth" in cookie)
        cookie_value = cookie["auth"].value
        expected_value = decode_signed_value("foobar", "auth", cookie_value)
        self.assertEqual("token", expected_value.decode("utf-8"))

    def test_cookie_credentials_plaintext(self):
        fetch_arguments = build_fetch_arguments("/foobar")
        credentials = CookieCredentials("auth", "token")
        credentials(fetch_arguments)
        cookie = SimpleCookie()
        cookie.load(fetch_arguments.headers["Cookie"])
        self.assertTrue("auth" in cookie)
        self.assertEqual("token", cookie["auth"].value)
