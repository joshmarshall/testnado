from testnado import AuthenticatedFetchCase
from tornado.testing import AsyncHTTPTestCase


class HandlerTestCase(AuthenticatedFetchCase, AsyncHTTPTestCase):
    pass
