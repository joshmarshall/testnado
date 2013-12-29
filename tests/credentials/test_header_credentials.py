from testnado.credentials.header_credentials import HeaderCredentials
from testnado.credentials.helpers import build_fetch_arguments
import unittest


class TestHeaderCredentials(unittest.TestCase):

    def test_header_credentials(self):
        fetch_arguments = build_fetch_arguments("/foo")

        credentials = HeaderCredentials({
            "X-Auth-Token": "foobar"
        })

        credentials(fetch_arguments)
        self.assertEqual("foobar", fetch_arguments.headers["X-Auth-Token"])

    def test_header_credentials_existing_headers(self):
        fetch_arguments = build_fetch_arguments(
            "/foo", headers={"X-Auth-Token": "whatever"})
        credentials = HeaderCredentials({
            "X-Auth-Token": "foobar",
        })
        credentials(fetch_arguments)
        self.assertEqual("whatever", fetch_arguments.headers["X-Auth-Token"])
