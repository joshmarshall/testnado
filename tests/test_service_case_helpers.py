import json

from tornado.httpclient import AsyncHTTPClient
from tornado.testing import gen_test, AsyncTestCase

from tests.helpers import TestCaseTestCase
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
                self.assertEqual({"foo": "bar"}, json.loads(response.body))

        self.execute_case(BasicTest)
