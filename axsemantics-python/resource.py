import json

import requests


def create_object(data, api_token, type=None):
    types = {
        'contentproject': ContentProject,
        'thing': Thing,
    }

    if isinstance(data, list):
        return [create_object(element, api_token, type=type) for element in data]
    elif isinstance(data, dict) and not isinstance(data, AXSemanticsObject):
        data = data.copy()
        id = data.get('id')

        class_name = type or data.get('type')
        _class = types.get(class_name, AXSemanticsObject)
        return _class.create_from_dict(data, api_token)
    else:
        return data


def _get_update_dict(current, previous):
    if isinstance(current, dict):
        previous = previous or {}
        diff = current.copy()
        for key in set(previous.keys()) - set(current.keys()):
            diff[key] = ""
        return diff
    return current if current is not None else ""


class RequestHandler:
    def __init__(self, token=None, api_base=None):
        self.base = api_base
        self.token = token

    def request(self, method, call_url, params, user_headers=None):
        url = '{}{}'.format(self.base, call_url)
        if method == 'get' or method == 'delete':
            if params:
                url += self.encode_params(params)
            post_data = None
        elif method == 'post':
            post_data = params
        else:
            return None

        headers = {
            'User-Agent': 'AXSemantics Python Client',
            'Authorization': 'Token {}'.format(self.token),
        }

        if user_headers:
            headers.update(user_headers)

        result = requests.request(method, url, headers=headers, data=post_data, timeout=80, verify=False)

        content = result.content.decode('utf-8') if hasattr(result.content, 'decode') else result.content
        content = json.loads(content)

        if result.status_code == 200:
            return content
        else:
            return result


    def encode_params(self, params):
        if isinstance(params, dict):
            return '?' + self._dict_encode(params)
        if isinstance(params, list):
            return '?' + '&'.join(self._dict_encode(d) for d in params)

    def _dict_encode(self, data):
        result = []
        for key, value in data.iteritems():
            result.append('{}={}'.format(key, value))
        return '&'.join(result)




class AXSemanticsObject(dict):
    def __init__(self, id, api_token=None, **kwargs):
        super(AXSemanticsObject, self).__init__()
        self._unsaved_attributes = set()
        self._params = kwargs
        self._previous = None

        self['id'] = id
        object.__setattr__(self, 'api_token', api_token)

    def update(self, update_dict):
        for key in update_dict:
            self._unsaved_attributes.add(key)
        return super(AXSemanticsObject, self).update(update_dict)

    def __setitem__(self, key, value):
        self._unsaved_attributes.add(key)
        return super(AXSemanticsObject, self).__setitem__(key, value)

    def __delitem__(self, key):
        self._unsaved_attributes.remove(key)
        return super(AXSemanticsObject, self).__delitem__(key)

    @classmethod
    def create_from_dict(cls, data, api_token):
        instance = cls(data.get('id'), api_token=api_token)
        instance.load_data(data, api_token=api_token)
        return instance

    def load_data(self, data, api_token=None, partial=False):
        self.api_token = api_token or getattr(data, 'api_token', None)

        if partial:
            self._unsaved_attributes -= set(data)
        else:
            self._unsaved_attributes = set()
            self.clear()

        for key, value in data.iteritems():
            super().__setitem__(key, create_object(value, api_token))

        self._previous = data

    @classmethod
    def api_base(cls):
        return None

    def request(self, method, url, params=None, headers=None):
        params = params or slef._retrieve_params
        requestor = api_requestor.APIRequestor(key=self.api_token, api_base = self.api_base())
        response, key = requestor.request(method, url, params, headers)
        return create_object(response, key)


class APIResource(AXSemanticsObject):
    @classmethod
    def retrieve(cls, id, api_key=None, **params):
        instance = cls(id, api_key, **params)
        instance.refresh()
        return instance

    def refresh(self):
        self.refresh_from(self.request('get', self.instance_url()))
        return self

    @classmethod
    def class_name(cls):
        return str(urllib.quote_plus(cls.__name__.lower()))

    @classmethod(cls)
    def class_url(cls):
        return '/v1/{}s'.format(cls.class_name())

    def instance_url(self):
        id = self.get('id')
        return '{}/{}'.format(self.class_url(), urllib.quote_plus(id))


class ListObject(AXSemanticsObject):
    def list(self, **params):
        return self.request('get', self['url'],  params)

    def auto_paging_iter(self):
        page = self
        params = dict(self._retrieve_params)

        while True:
            item_id = None
            for item in page:
                item_id = item.get('id', None)
                yield item

            if not getattr(page, 'has_more', False) or item_id is None:
                return

            params['starting_after'] = item_id
            page = self.list(**params)

    def retrieve(self, id, **params):
        base = self.get('url')
        url = '{}/{}'.format(base, urllib.quote_plus(id))
        return self.request('get', url, params)

    def __iter__(self):
        return getattr(self, 'data', []).__iter__()




class ContentProject:
    pass
