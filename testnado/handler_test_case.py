from testnado import AuthenticatedFetchCase
from tornado.testing import AsyncHTTPTestCase
import urlparse


class HandlerTestCase(AuthenticatedFetchCase, AsyncHTTPTestCase):

    def assert_redirected_path_equals(self, expected_path, response):
        if "Location" not in response.headers:
            self.fail("Response does not have a 'Location' header.")
        location = response.headers["Location"]
        path = urlparse.urlparse(location).path
        self.assertEqual(expected_path, path)
