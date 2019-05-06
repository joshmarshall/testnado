import json

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import AsyncTestCase, gen_test, bind_unused_port

from testnado.mock_service import MockService


class TestMockService(AsyncTestCase):

    def setUp(self):
        super(TestMockService, self).setUp()
        self.service = MockService(self.io_loop)

    def test_mock_service_url_helpers(self):
        host = "localhost:{0}".format(self.service.port)
        self.assertEqual("http", self.service.protocol)
        self.assertEqual("http://" + host, self.service.base_url)
        self.assertEqual("http://" + host + "/foo", self.service.url("/foo"))

    @gen.coroutine
    def fetch(self, url, *args, **kwargs):
        kwargs.setdefault("raise_error", False)
        client = AsyncHTTPClient()
        response = yield client.fetch(url, *args, **kwargs)
        raise gen.Return(response)

    @gen_test
    def test_mock_service_add_method(self):
        self.service.add_method("GET", "/", lambda x: x.finish({"num": 5}))
        self.service.add_method("POST", "/", lambda x: x.finish("RESPONSE"))
        self.service.listen()

        response = yield self.fetch(self.service.url("/"))
        self.assertEqual(200, response.code)
        self.assertEqual({"num": 5}, json.loads(response.body.decode("utf-8")))

        response = yield self.fetch(
            self.service.url("/"), method="POST", body="FOOBAR")
        self.assertEqual(200, response.code)
        self.assertEqual("RESPONSE", response.body.decode("utf-8"))

        response = yield self.fetch(self.service.url("/"), method="OPTIONS")
        self.assertEqual(405, response.code)

        response = yield self.fetch(self.service.url("/foo"))
        self.assertEqual(404, response.code)

    @gen_test
    def test_mock_service_assert_requested(self):
        self.service.listen()
        # it should 501 all routes and methods by default, so
        # it functions as a simple mocking tool but still makes people
        # actually put content in for real client testing
        response = yield self.fetch(
            self.service.url("/foobar?query=true"), method="OPTIONS")
        self.assertEqual(501, response.code)
        request = self.service.assert_requested("OPTIONS", "/foobar")
        self.assertTrue("query" in request.arguments)

    @gen_test
    def test_mock_service_assert_requested_ignores_headers_by_default(self):
        self.service.listen()
        response = yield self.fetch(
            self.service.url("/foobar?query=true"), method="GET",
            headers={"X-Foo": "Bar"})
        self.assertEqual(501, response.code)
        request = self.service.assert_requested("GET", "/foobar")
        self.assertTrue("query" in request.arguments)
        self.assertEqual("Bar", request.headers["X-Foo"])

    @gen_test
    def test_mock_service_assert_not_requested(self):
        self.service.listen()
        self.service.assert_not_requested("GET", "/foobar")

        yield self.fetch(self.service.url("/foobar"))

        with self.assertRaises(AssertionError):
            self.service.assert_not_requested("GET", "/foobar")

    @gen_test
    def test_mock_service_assert_requested_with_headers(self):
        self.service.listen()
        response = yield self.fetch(
            self.service.url("/foobar"), headers={"x-thing": "foobar"})
        self.assertEqual(501, response.code)
        self.service.assert_requested(
            "GET", "/foobar", headers={"X-Thing": "foobar"})

    @gen_test
    def test_mock_service_assert_requested_supports_delete(self):
        self.service.add_method("DELETE", "/", lambda x: x.finish({"x": True}))
        self.service.listen()

        response = yield self.fetch(self.service.url("/"), method="DELETE")
        self.assertEqual(200, response.code)
        self.service.assert_requested("DELETE", "/")

    @gen_test
    def test_mock_service_assert_requested_supports_head(self):
        self.service.add_method("HEAD", "/", lambda x: x.finish({"x": True}))
        self.service.listen()

        response = yield self.fetch(self.service.url("/"), method="HEAD")
        self.assertEqual(200, response.code)
        self.service.assert_requested("HEAD", "/")

    @gen_test
    def test_mock_service_assert_requested_supports_nontstandard_methods(self):
        self.service.add_method("FOOBAR", "/", lambda x: x.finish({"x": True}))
        self.service.listen()

        response = yield self.fetch(
            self.service.url("/"), method="FOOBAR",
            allow_nonstandard_methods=True)

        self.assertEqual(200, response.code)
        self.service.assert_requested("FOOBAR", "/")

    @gen_test
    def test_mock_service_assert_stop_stops_the_service(self):
        self.service.listen()
        self.service.stop()

        response = yield self.fetch(self.service.url("/"), method="HEAD")
        self.assertEqual(599, response.code)

    @gen_test
    def test_mock_service_listen_listens_to_specified_port_number(self):
        sock, port = bind_unused_port()
        sock.close()
        service = MockService(self.io_loop, port)
        service.add_method("GET", "/", lambda x: x.finish("use this port"))

        service.listen()

        response = yield self.fetch(service.url("/"))
        self.assertEqual(200, response.code)
        self.assertEqual("use this port", response.body.decode("utf-8"))

        host = "localhost:{0}".format(port)
        self.assertEqual("http", service.protocol)
        self.assertEqual(port, service.port)
        self.assertEqual("http://" + host, service.base_url)
        self.assertEqual("http://" + host + "/foo", service.url("/foo"))

    @gen_test
    def test_mock_service_listen_adds_socket_when_initialized_with_tuple_port(self):
        sock, port = bind_unused_port()
        service = MockService(self.io_loop, (sock, port))
        service.add_method("GET", "/", lambda x: x.finish("it worked"))

        service.listen()

        response = yield self.fetch("http://localhost:{0}/".format(port))
        self.assertEqual(200, response.code)
        self.assertEqual("it worked", response.body.decode("utf-8"))

        host = "localhost:{0}".format(port)
        self.assertEqual("http", service.protocol)
        self.assertEqual(port, service.port)
        self.assertEqual("http://" + host, service.base_url)
        self.assertEqual("http://" + host + "/foo", service.url("/foo"))
