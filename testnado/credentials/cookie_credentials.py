import Cookie
from tornado.web import create_signed_value


class CookieCredentials(object):

    def __init__(self, cookie_name, cookie_value, cookie_secret=None):
        # need to update this so it takes values like domain, expires, etc
        # for people who test more deeply.

        self._cookie = Cookie.SimpleCookie()
        self._cookie_name = cookie_name
        if cookie_secret:
            cookie_value = create_signed_value(
                cookie_secret, cookie_name, cookie_value)
        self._cookie[cookie_name] = cookie_value

    def __call__(self, fetch_arguments):
        cookie_string = self._cookie[self._cookie_name].OutputString(None)
        fetch_arguments.headers.setdefault("Cookie", cookie_string)
