from testnado import HandlerTestCase
from tests.helpers import TestCaseTestCase
from tornado.web import Application, RequestHandler


class TestHandlerTestCase(TestCaseTestCase):

    def test_handler_test_case_get_app(self):

        class TestHandlerTestCaseNoApp(HandlerTestCase):
            def test_thing(self):
                self.fail(
                    "Tornado AsyncHTTPTestCase should fail before this "
                    " because get_app() has not been implemented.")

        with self.assertRaises(NotImplementedError):
            self.execute_case(TestHandlerTestCaseNoApp)

    def test_handler_test_case_get_credentials(self):

        class TestHandlerTestCaseNoCredentials(HandlerTestCase):

            def get_app(self):
                return Application()

            def test_auth(self):
                with self.assertRaises(NotImplementedError):
                    self.authenticated_fetch("/secret")

        self.execute_case(TestHandlerTestCaseNoCredentials)

    def test_handler_assert_redirected_path_equals(self):

        class Handler(RequestHandler):
            def get(self):
                self.redirect("http://google.com/location")

        class TestHandlerAssertRedirect(HandlerTestCase):

            def get_app(self):
                return Application([("/redirect", Handler)])

            def test_redirect(self):
                response = self.fetch("/redirect")
                self.assert_redirected_path_equals("/location", response)

        self.execute_case(TestHandlerAssertRedirect)

    def test_handler_assert_redirected_path_mismatch_query_raises(self):

        class Handler(RequestHandler):
            def get(self):
                self.redirect("http://google.com/foobar")

        class TestHandlerAssertRedirect(HandlerTestCase):

            def get_app(self):
                return Application([("/redirect", Handler)])

            def test_redirect(self):
                response = self.fetch("/redirect")
                self.assert_redirected_path_equals("/location", response)

        with self.assertRaises(AssertionError):
            self.execute_case(TestHandlerAssertRedirect)
