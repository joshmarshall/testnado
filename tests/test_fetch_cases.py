# These tests are fairly obscure. Any help making them more clear
# would be appreciated.

from tests.helpers import TestCaseTestCase
from testnado import FetchCase, AuthenticatedFetchCase
from tornado.testing import AsyncHTTPTestCase
import tornado.web


class Handler(tornado.web.RequestHandler):

    def get(self):
        if self.request.headers.get("foobar") == "authed":
            return self.redirect("/authed")
        return self.redirect("/public")


class BasicAppTestCase(AsyncHTTPTestCase):

    def get_app(self):
        return tornado.web.Application([("/foo", Handler)])


class TestFetchCases(TestCaseTestCase):

    def test_handler_test_case_fetch_no_redirect(self):
        @self.build_case(FetchCase, BasicAppTestCase)
        def test_fetch_no_redirect(self):
            response = self.fetch("/foo")
            self.assertEqual(302, response.code)
            self.assertEqual("/public", response.headers["Location"])
            self.assertIsNotNone(response)

    def test_authenticated_fetch_get_credentials_raises(self):
        with self.assertRaises(NotImplementedError):
            @self.build_case(AuthenticatedFetchCase, BasicAppTestCase)
            def test_authenticated_fetch(self):
                self.authenticated_fetch("/foo")

    def test_authenticated_fetch_get_credentials(self):

        class DummyCredentials(object):

            def get_credentials(self):
                def update_credentials(fetch_arguments):
                    fetch_arguments.headers["foobar"] = "authed"
                return update_credentials

        @self.build_case(
            DummyCredentials, AuthenticatedFetchCase,
            BasicAppTestCase)
        def test_method(self):
            response = self.authenticated_fetch("/foo")
            self.assertEqual(302, response.code)
            self.assertEqual("/authed", response.headers["Location"])
