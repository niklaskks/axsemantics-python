import requests

from axsemantics import constants
from axsemantics.errors import (
    APIConnectionError,
    APIError,
)


class RequestHandler:
    def __init__(self, token=None, api_base=None):
        self.base = api_base or constants.API_BASE
        self.token = token

    def request(self, method, url, params, user_headers=None):
        url = '{}{}'.format(self.base, url)
        token = self.token or constants.API_TOKEN

        if method in ('get', 'delete') and params:
            url += self.encode_params(params)

        headers = {
            'User-Agent': 'AXSemantics Python Client',
            'Content-Type': 'application/json',
        }

        if token:
            headers.update({'Authorization': 'Token {}'.format(token)})

        if user_headers:
            headers.update(user_headers)

        if constants.DEBUG:
            print('Sending {} request to {}.'.format(method, url))

        try:
            if method == 'post':
                result = requests.post(url, headers=headers, json=params, timeout=5)
            elif method == 'put':
                result = requests.put(url, headers=headers, data=params, timeout=5)
            else:
                result = requests.request(method, url, headers=headers, timeout=5)

            result.raise_for_status()

        except (requests.Timeout, requests.ConnectionError):
            raise APIConnectionError

        except requests.HTTPError:
            if constants.DEBUG:
                print('Got unexpected reponse with status {}.'.format(result.status_code))
                print('Content: {}'.format(result.content))

            raise APIError(result)

        return result.json()

    def encode_params(self, params):
        if isinstance(params, dict):
            return '?' + self._dict_encode(params)
        if isinstance(params, list):
            return '?' + '&'.join(self._dict_encode(d) for d in params)

    def _dict_encode(self, data):
        return '&'.join(
            '{}={}'.format(key, value)
            for key, value in data.items()
        )
