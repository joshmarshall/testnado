# TESTNADO

This is a collection of several testing helpers I've compiled for Tornado,
including authenticated fetch()ing, mock APIs, and running Selenium sessions
locally against Tornado applications.

[![Build Status](https://travis-ci.org/joshmarshall/testnado.png?branch=master)](https://travis-ci.org/joshmarshall/testnado)

## Installation
Install with:

```bash
pip install testnado
```

... or if you are running bleeding edge, just:

```bash
pip install ./
```

... from the downloaded / cloned directory.

## Usage
Most usage is as simple as, inside your tests, subclassing from HandlerTestCase
instead of AsyncHTTPTestCase.

```python
from testnado import HandlerTestCase
from testnado.credentials import HeaderCredentials
from tornado.web import Application

class MyHandlerTestCase(HandlerTestCase):

    def setUp(self):
        super(MyHandlerTestCase, self).setUp()
        # create your dummy user, however you want.
        self._user = User.create(...)

    def tearDown(self):
        super(MyHandlerTestCase, self).tearDown()
        # clean up your database, or whatever you used.
        self._user.delete_forever_haha()

    def get_app(self):
        return Application(["/", MyIndexHandler])

    def get_credentials(self):
        # return a credentials object that updates a
        # response object with the proper stuff
        return HeaderCredentials({"X-Auth-Token": self._user.token})
```

`testnado.HandlerTestCase` is a simple facade in front of composing more
complicated test case behavior, like:

```python
from tornado.testing import AsyncHTTPTestCase
from testnado import AuthenticatedFetchCase

class MyHandlerTestCase(AuthenticatedFetchCase, AsyncHTTPTestCase):
    ...
```

Once you've defined all your authentication requirements, this is obviously
most helpful as a shared base class for all your Handler test cases, so writing
tests is simpler:

```python
from mytests.helpers import MyHandlerTestCase

class TestAwesomeAuthorization(MyHandlerTestCase):

    def test_auth(self):
        response = self.authenticated_fetch("/secret_resource")
        self.assertEqual(200, response.code)

    def test_auth_response(self):
        resource = Resource.create(user=self._user)
        response = self.authenticated_fetch("/" + resource.id)
        self.assertEqual(resource.view(), json.loads(response.body))
```

## Credentials
At it's core, `HandlerTestCase.get_credentials()` just returns a callable. That
callable will receive one argument of `fetch_arguments`, which is a named tuple
with various fetch() parameters. This should be updated in place. For instance:

```python

def get_credentials(self):
    def callback(fetch_arguments):
        fetch_arguments.headers.setdefault("Cookie", "token=FOOBAR")
        fetch_arguments.auth_username = "foo@bar.com"
        fetch_arguments.auth_password = "foobar"
        fetch_arguments.auth_mode = "basic"
    return callback

```

Of course, that's annoying, especially for more boilerplate-y use cases like
secure cookies and safe header overwriting. For that reason, I've provided a
few functor helpers (like HeaderCredentials above).

```
from testnado.credentials import CookieCredentials

class MyHandlerTestCase(HandlerTestCase):

    def get_app(self):
        return Application(..., cookie_secret="foobar")

    def get_credentials(self):
        return CookieCredentials("auth", "token", cookie_secret="foobar")
```

Much shorter. I'll probably add a BasicAuthCredentials, but c'mon, how lazy are
we. :)

## Mocking out API Services
The intent of MockService (and test case helpers) is to create fake API
services that your libraries need to talk to (and you need to fake working /
not-working responses). So in general, you'll be:

* Creating a service
* Attaching routes / responses to it
* Passing the service URL to clients
* Starting the service before initiating everything else

```python
from tornado.testing import AsyncTestCase, gen_test
from testnado.service_case_helpers import ServiceCaseHelpers

from mylib.api_client import APIClient


class TestAPIClient(ServiceCaseHelpers, AsyncTestCase):

    @gen_test
    def test_client(self):
        responder = lambda handler: handler.finish({"user": "joeuser"})

        service = self.add_service()
        service.add_method("POST", "/v1/accounts", responder)
        service.listen()

        client = APIClient(service.url("/v1"), self.io_loop)
        account = yield client.authenticate(my_app_token)
        # test the JSON result is used
        self.assertEqual("joeuser", account.username)
        service.assert_requested(
            "GET", "/v1/accounts", headers={"X-Token": my_app_token})
```

You can also instantiate a MockService yourself inside of another
test if you don't want the add_service() helpers. There are a few other
smaller things this does, but principally that's it. Read the source and
tests for more insight.

### Browser Testing (Removed) ###
The browser testing via Selenium section has been removed for Tornado 5 support
-- there were incompatibilities with the IOLoop and threading in the first
place, but with the migration away from PhantomJS, the implementation was not
necessary as part of testnado core. It may resurface as another library
dependent on this one in the future, which is a cleaner design anyway (not all
Tornado services should require a dev dependency of Selenium...)
