import json

from tornado.httpclient import AsyncHTTPClient
from tornado.testing import gen_test, AsyncTestCase

from tests.helpers import TestCaseTestCase, ServiceTestHelpers
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

        class BasicTest(ServiceCaseHelpers, AsyncTestCase, ServiceTestHelpers):

            @gen_test
            def test_stop_services(self):
                service1 = self.add_service()
                service2 = self.add_service()
                service3 = self.add_service()
                self.start_services()

                self.stop_services()
                yield self.assert_closed(service1.url("/"))
                yield self.assert_closed(service2.url("/"))
                yield self.assert_closed(service3.url("/"))

        self.execute_case(BasicTest)
