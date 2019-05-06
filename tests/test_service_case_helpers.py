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
            def test_add_method(self):
                service = self.add_service()
                service.add_method("GET", "/endpoint", handle_get)
                self.start_services()
                client = AsyncHTTPClient()
                response = yield client.fetch(service.url("/endpoint"))
                self.assertEqual(200, response.code)
                self.assertEqual(
                    {"foo": "bar"},
                    json.loads(response.body.decode("utf-8")))

        self.execute_case(BasicTest)

    def test_service_case_helpers_add_service_accepts_existing_service(self):

        def handle_get(handler):
            handler.finish({"foo": "bar"})

        class BasicTest(ServiceCaseHelpers, AsyncTestCase):

            @gen_test
            def test_add_method(self):
                service = MockService(self.io_loop)
                service.add_method("GET", "/endpoint", handle_get)
                self.add_service(service)
                self.start_services()
                client = AsyncHTTPClient()
                response = yield client.fetch(service.url("/endpoint"))
                self.assertEqual(200, response.code)
                self.assertEqual(
                    {"foo": "bar"},
                    json.loads(response.body.decode("utf-8")))

        self.execute_case(BasicTest)

    def test_service_case_helpers_stop_services_stops_all_services(self):

        def handle_get(handler):
            handler.finish({"foo": "bar"})

        class BasicTest(ServiceCaseHelpers, AsyncTestCase):

            @gen_test
            def test_stop_services(self):
                service1 = self.add_service()
                service2 = self.add_service()
                service3 = self.add_service()
                self.start_services()

                self.stop_services()

                client = AsyncHTTPClient()

                self.assertEqual(
                    599, (yield client.fetch(service1.url("/"), raise_error=False)).code)
                self.assertEqual(
                    599, (yield client.fetch(service2.url("/"), raise_error=False)).code)
                self.assertEqual(
                    599, (yield client.fetch(service3.url("/"), raise_error=False)).code)

        self.execute_case(BasicTest)
