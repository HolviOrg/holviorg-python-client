# -*- coding: utf-8 -*-
import cookielib
import urllib2
import json

from exceptions import HolviUnknownException, HolviURLException, HolviCryptException, HolviException, HolviDataItemException
import holvi.exceptions as exceptions

class Connection(object):
    """Connection provides methods for communicating with Holvi server

    """
    __API_VERSION__ = "1.0"

    def __init__(self, server_url):
        """Initializer for Connection

        :param server_url: Server used for requests

        """
        self._server_url = server_url
        self._cookies = cookielib.CookieJar()
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookies))
        self._is_authed = False

    def auth(self, username, auth_data, auth_method, apikey):
        """Authenticates connection with given credentials

        :param username: Username used for authentication
        :param auth_data: Password used for authentication
        :param auth_method: Authentication method to be used
        :param apikey: Client's API-key

        """
        method = "auth"
        params = {
                    "username": username,
                    "auth_data": auth_data,
                    "auth_method": auth_method,
                    "apikey": apikey
                }
        response = self.make_request(method, params)
        if response['result'] == 'success':
            self._is_authed = True
        else:
            self._is_authed = False
            self._handle_exception(response)

    def make_request(self, method, params):
        """Sends request to Holvi server with given method and parameters

        :param method: Operation to be performed on server
        :param params: Parameters for given method

        Sends a request to Holvi server and returns the result if the operation
        was succesful.

        """
        url = self._server_url + "/api/" + self.__API_VERSION__ + "/json"
        json_request = {
                "method": method,
                "params": params
                }
        response = self._opener.open(url, json.JSONEncoder().encode(json_request))
        response = json.JSONDecoder().decode(response.read())
        if response['result'] == 'success':
            return response
        else:
            self._handle_exception(response)

    def make_transaction(self, headers, url_suffix, data = None):
        """Creates a transaction (download / upload) to Holvi server.

        :param headers: Headers to be added to the request
        :param url_suffix: '/store', '/fetch' depending on the direction of the transaction
        :param data: Data chunk to be added to request when POSTing data

        Sends the request with given headers to Holvi server.
        """
        url = self._server_url + "/api/" + self.__API_VERSION__ + url_suffix
        request = urllib2.Request(url)
        self._cookies.add_cookie_header(request)
        for key in headers:
            request.add_header(key, headers[key])
        request.data = data
        response = urllib2.urlopen(request)

        result = response.headers.get('X-HOLVI-RESULT')
        if result == 'OK':
            return response
        else:
            err_type, err_id, err_message = result.split(' ', 2)  # Format is 'ERROR: Err# ErrMessage'
            raise HolviDataItemException(err_id, err_message)

    def make_query(self, headers, url_suffix='/fetch'):
        """Makes a HEAD request to Holvi server to retrieve DataItem information

        :param headers: Headers to be addes to the request
        :param url_suffix: '/fetch'

        Sends the HEAD request with given headers to the Holvi server.
        Returns response headers if succesful.
        """
        url = self._server_url + "/api/" + self.__API_VERSION__ + url_suffix
        request = urllib2.Request(url)
        request.get_method = lambda : 'HEAD'
        self._cookies.add_cookie_header(request)
        for key in headers:
            request.add_header(key, headers[key])

        response = urllib2.urlopen(request)
        result = response.headers.get('X-HOLVI-RESULT')
        if result != 'OK':
            err_type, err_id, err_message = result.split(' ', 2)  # Format is 'ERROR: Err# ErrMessage'
            raise HolviDataItemException(err_id, err_message)
        return response.headers

    def _handle_exception(self, response):
        """Handles the exceptions in request responses

        :param response: The response to be parsed for exceptions

        Parses the exception from response and raises correct exception.
        """
        exception = response.get('exception')
        if not exception:
            print response
            raise HolviUnknownException()

        message = exception.get('message')
        id_ = exception.get('id')
        type_ = exception.get('type')

        if hasattr(exceptions, type_):
            raise getattr(exceptions, type_)(id_, message)
        else:
            print response
            raise HolviUnknownException()

#   def _handle_transaction_exception(self, exception):
#       """Handles the exceptions occured during transactions
#       :param exception:
#       """
#       id_ = exception.code
#       message = exception.msg
#       raise HolviURLException(id_, message)

