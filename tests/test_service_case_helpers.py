import json

from tornado.httpclient import AsyncHTTPClient
from tornado.testing import gen_test, AsyncTestCase, bind_unused_port

from tests.helpers import TestCaseTestCase
from testnado.mock_service import MockService
from testnado.service_case_helpers import ServiceCaseHelpers


class TestServiceTestCase(TestCaseTestCase):

    def test_service_case_helpers_add_service(self):

        def handle_get(handler):
            handler.finish({"foo": "bar"})

        class BasicTest(ServiceCaseHelpers, AsyncTestCase):

            @gen_test
            def test_add_route(self):
                service = self.add_service()
                service.add_method("GET", "/endpoint", handle_get)
                self.start_services()
                client = AsyncHTTPClient(io_loop=self.io_loop)
                response = yield client.fetch(service.url("/endpoint"))
                self.assertEqual(200, response.code)
                self.assertEqual(
                    {"foo": "bar"},
                    json.loads(response.body.decode("utf-8")))

        self.execute_case(BasicTest)

    def test_service_case_helpers_add_service_allows_optional_argument(self):

        def handle_get(handler):
            handler.finish({"foo": "bar"})

        class BasicTest(ServiceCaseHelpers, AsyncTestCase):

            @gen_test
            def test_add_route(self):
                s, port = bind_unused_port()
                s.close()
                service = MockService(self.io_loop, port)
                service.add_method("GET", "/endpoint", handle_get)
                self.add_service(service)
                self.start_services()
                client = AsyncHTTPClient(io_loop=self.io_loop)
                response = yield client.fetch(service.url("/endpoint"))
                self.assertEqual(200, response.code)
                self.assertEqual(
                    {"foo": "bar"},
                    json.loads(response.body.decode("utf-8")))

        self.execute_case(BasicTest)
