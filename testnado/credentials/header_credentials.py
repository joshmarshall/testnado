class HeaderCredentials(object):

    def __init__(self, headers):
        self._headers = headers

    def __call__(self, fetch_arguments):
        for header_key, header_value in self._headers.items():
            fetch_arguments.headers.setdefault(header_key, header_value)
