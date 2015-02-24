from tornado.testing import bind_unused_port
from testnado.mock_service import MockService


class ServiceCaseHelpers(object):
    # this mixin must be used with an AsyncHTTPTestCase or AsyncTestCase

    @property
    def mock_services(self):
        if not hasattr(self, "_mock_services"):
            self._mock_services = []
        return self._mock_services

    def add_service(self):
        _, port = bind_unused_port()
        service = MockService(self.io_loop, port)
        self.mock_services.append(service)
        return service

    def start_services(self):
        for service in self.mock_services:
            service.listen()
