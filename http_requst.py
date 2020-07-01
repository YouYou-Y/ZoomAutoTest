from http.client import IncompleteRead

#from misc.utils import *
import urllib.request
from urllib.error import HTTPError, URLError
import json
from socket import timeout
# from misc.global_vars import *

HTTP_REQUEST_METHODS = ['GET', 'POST', 'DELETE', 'PUT']


class HttpRequest:
    def __init__(self, url, logger=None):
        self.url = url
        self.logger = logger
        self.response = 'N/A'
        self.headers = {}
        self.data = None
        self.http_status_code = 0
        self.timeout = 15.0
        self.error = ''
        self.method = 'GET'

    def set_logger(self, logger):
        self.logger = logger

    def set_timeout(self, api_timeout):
        self.timeout = api_timeout

    def is_valid_http_request_method(self):
        if self.method not in HTTP_REQUEST_METHODS:
            if self.logger is not None:
                self.logger.info(f'HttpRequest.request, invalid http request method: {self.method}')
            return False
        return True

    def retrieve_http_headers(self, headers):
        if headers is not None:
            self.headers = {k.lower(): v for k, v in headers.items()}

    def retrieve_body_data(self, body):
        if 'content-type' in self.headers:
            if body is not None:
                content_type = str(self.headers['content-type']).lower()
                if 'application/json' in content_type:
                    self.data = json.dumps(body).encode('utf-8')

        if body is not None and self.data is None:
            self.data = f'{body}'.encode()

    def request(self, headers: dict = None, body=None, method='GET'):
        api_result = False

        self.method = method.upper()
        if not self.is_valid_http_request_method():
            return api_result

        self.retrieve_http_headers(headers)
        self.retrieve_body_data(body)

        try:
            if self.logger is not None:
                self.logger.info(f'HttpRequest.request, begin call url [{self.method}]: {self.url}')
            req = urllib.request.urlopen(urllib.request.Request(self.url, headers=self.headers, data=self.data, method=self.method), timeout=self.timeout)
            self.http_status_code = req.getcode()
            if self.logger is not None:
                self.logger.info(f'HttpRequest.request, end call url [{self.method}]: {self.url},  http_status_code: {self.http_status_code}')
            # self.response = json.loads(req.read().decode())
            if self.http_status_code == 200 or self.http_status_code == 201:
                if self.logger is not None:
                    self.logger.info(f'HttpRequest.request, begin read data from response')
                # read will raise IncompleteRead exception, try to catch it to check if we can fix read freeze issue
                try:
                    self.response = req.read().decode('utf-8')
                    api_result = True
                except IncompleteRead as e:
                    api_result = False
                    self.error = f'read response error: {e}'
                    if self.logger is not None:
                        self.logger.error(f'HttpRequest.request, read error: {e}')
                if self.logger is not None:
                    self.logger.info(f'HttpRequest.request, end read data from response')
            else:
                self.error = f'Invalid http status code: {self.http_status_code}'
                try:
                    self.response = req.read().decode('utf-8')
                except Exception:
                    pass
        except (HTTPError, URLError) as e:
            try:
                self.http_status_code = e.getcode()
                self.response = e.read().decode('utf-8')
            except Exception:
                pass
            self.error = f'{e}'
            if self.logger is not None:
                self.logger.error(f'HttpRequest.request, URLError occurred: {self.error}, response:{self.response}')
        except timeout:
            self.error = f'http request timeout after: {self.timeout} seconds'
            try:
                self.response = e.read().decode('utf-8')
            except Exception:
                pass
            if self.logger is not None:
                self.logger.error(f'HttpRequest.request, timeout exception occurred: {self.error}, response:{self.response}')

        return api_result
