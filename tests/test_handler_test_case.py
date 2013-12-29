from testnado import HandlerTestCase
from tests.helpers import TestCaseTestCase
from tornado.web import Application


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
