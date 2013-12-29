# Yes, these are test helpers for a test helper library that is being
# tested. It contains a class called TestCaseTestCase. Meta enough yet?

from tornado.web import Application
import unittest


class TestCaseTestCase(unittest.TestCase):

    def build_case(self, *bases):
        """
        This decorator runs the decorated test function, with the case
        instance provided as the first argument. For instance:

        @self.execute_case()
        def test_thing(self):
            self.fetch("/path")

        ... is the same as creating a new HandlerTestCase subclass,
        instantiating it, and then calling debug. Just a shortcut.
        """

        if not bases:
            self.fail("Missing bases for 'build_case'")

        def wrapper(test_method):
            def get_app(self):
                return Application()

            def test_the_method(case_instance):
                test_method(case_instance)

            methods = {
                "get_app": get_app,
                "test_the_method": test_the_method
            }

            Case = type("Case", bases, methods)
            self.execute_case(Case)

        return wrapper

    def execute_case(self, test_case):
        """
        Executes a test case. The test case can only contain one test
        method.

        """
        use_method = None
        for method in dir(test_case):
            if not callable(getattr(test_case, method)):
                continue
            if not method.startswith("test_"):
                continue
            if use_method:
                self.fail(
                    "Test case '%s' has more than one test method." % (
                        test_case.__name__))
            use_method = method

        test_case(use_method).debug()
