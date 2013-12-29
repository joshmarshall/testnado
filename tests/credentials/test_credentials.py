from testnado.credentials.helpers import build_fetch_arguments
import unittest


class TestBuildFetchArguments(unittest.TestCase):

    def test_build_fetch_arguments_default(self):
        fetch_arguments = build_fetch_arguments("/foo")
        self.assertEqual("/foo", fetch_arguments.path)
        self.assertEqual({}, fetch_arguments.headers)
        self.assertEqual(None, fetch_arguments.body)
        self.assertEqual(None, fetch_arguments.auth_mode)
        self.assertEqual(None, fetch_arguments.auth_username)
        self.assertEqual(None, fetch_arguments.auth_password)

    def test_build_fetch_arguments_overwrite(self):
        fetch_arguments = build_fetch_arguments("/foo", body="whatever")
        self.assertEqual("whatever", fetch_arguments.body)
