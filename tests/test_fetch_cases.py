# These tests are fairly obscure. Any help making them more clear
# would be appreciated.

import mock
from tests.helpers import TestCaseTestCase
from tornado.testing import AsyncHTTPTestCase as AHTC
from testnado import FetchCase, AuthenticatedFetchCase


class TestFetchCases(TestCaseTestCase):

    @mock.patch("tornado.testing.AsyncHTTPTestCase.fetch")
    def test_handler_test_case_fetch_no_redirect(self, mock_fetch):
        @self.build_case(FetchCase, AHTC)
        def test_fetch_no_redirect(self):
            self.fetch("/foo")

        mock_fetch.assert_called_with("/foo", follow_redirects=False)

    def test_authenticated_fetch_get_credentials_raises(self):
        with self.assertRaises(NotImplementedError):
            @self.build_case(AuthenticatedFetchCase, AHTC)
            def test_authenticated_fetch(self):
                self.authenticated_fetch("/secret")

    @mock.patch("tornado.testing.AsyncHTTPTestCase.fetch")
    def test_authenticated_fetch_get_credentials(self, mock_fetch):

        class DummyCredentials(object):

            def get_credentials(self):
                def update_credentials(fetch_arguments):
                    fetch_arguments.headers["foobar"] = "authed"
                return update_credentials

        @self.build_case(DummyCredentials, AuthenticatedFetchCase, AHTC)
        def test_method(self):
            self.authenticated_fetch("/secret")

        mock_fetch.assert_called_with(
            url="/secret", headers={"foobar": "authed"},
            follow_redirects=False)
