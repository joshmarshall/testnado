from tornado.testing import AsyncTestCase, gen_test, get_unused_port
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.web import RequestHandler, Application

from testnado.mock_client import MockClient, MissingMockResponse


class TestMockClient(AsyncTestCase):

    def setUp(self):
        super(TestMockClient, self).setUp()
        self.mock_client = MockClient(self.io_loop)

    @gen_test
    def test_patches_known_hosts(self):
        self.mock_client.mock_url("http://foo.com/bar")
        with self.mock_client.patch():
            client = AsyncHTTPClient()
            response = yield client.fetch("http://foo.com/bar")

        self.assertEqual(200, response.code)
        self.assertEqual("", response.body)
        self.assertEqual(0, response.headers["Content-Length"])

    @gen_test
    def test_patches_allow_overwrite(self):
        response = self.mock_client.mock_url("http://foo.com/bar")
        response.code = 204
        response.body = "BODY"
        response.headers["X-Test"] = "foobar"

        with self.mock_client.patch():
            client = AsyncHTTPClient()
            fetched = yield client.fetch("http://foo.com/bar")

        self.assertEqual(204, fetched.code)
        self.assertEqual("BODY", fetched.body)
        self.assertEqual("foobar", fetched.headers["x-test"])

    @gen_test
    def test_patches_raises_error(self):
        response = self.mock_client.mock_url("http://foo.com/bar")
        response.code = 500
        response.body = "ERROR"

        with self.mock_client.patch():
            client = AsyncHTTPClient()
            with self.assertRaises(HTTPError) as exc_context:
                yield client.fetch("http://foo.com/bar")

        exception = exc_context.exception
        self.assertEqual(500, exception.code)
        self.assertEqual(5, exception.response.headers["Content-length"])

    @gen_test
    def test_patches_respects_raise_error_flag(self):
        response = self.mock_client.mock_url("http://foo.com/bar")
        response.code = 500

        with self.mock_client.patch():
            client = AsyncHTTPClient()
            fetched_response = yield client.fetch(
                "http://foo.com/bar", raise_error=False)

        self.assertEqual(500, fetched_response.code)

    @gen_test
    def test_patch_passes_through_unknown_requests(self):

        class Handler(RequestHandler):
            def get(self):
                self.finish("REAL RESPONSE")

        port = get_unused_port()
        app = Application([("/", Handler)])
        app.listen(port)
        with self.mock_client.patch():
            client = AsyncHTTPClient()
            response = yield client.fetch("http://localhost:{}/".format(port))

        self.assertEqual(200, response.code)
        self.assertEqual("REAL RESPONSE", response.body)

    @gen_test
    def test_patch_ignores_query_parameters(self):
        response = self.mock_client.mock_url("http://foo.com/bar")

        with self.mock_client.patch():
            client = AsyncHTTPClient()
            fetched_response = yield client.fetch("http://foo.com/bar?q=baz")

        self.assertEqual(fetched_response, response)

    @gen_test
    def test_patch_requires_multiple_mocks_for_multiple_requests(self):
        self.mock_client.mock_url("http://foo.com/one")
        # put two requests in for a second path
        self.mock_client.mock_url("http://foo.com/two")
        self.mock_client.mock_url("http://foo.com/two")

        with self.mock_client.patch():
            client = AsyncHTTPClient()
            yield client.fetch("http://foo.com/one")
            with self.assertRaises(MissingMockResponse):
                yield client.fetch("http://foo.com/one")

            yield client.fetch("http://foo.com/two")
            yield client.fetch("http://foo.com/two")
