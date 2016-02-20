import json

import requests

import constants


def authenticate(username, password, api_base=None):
    data = {
        'email': username,
        'password': password,
    }
    requestor = RequestHandler()
    response = requestor.request(url='/v1/rest-auth/login', method='post', params=data)

    constants.API_TOKEN = response['key']


def create_object(data, api_token=None, type=None):
    types = {
        'contentproject': ContentProject,
        'thing': Thing,
    }

    if isinstance(data, list):
        return [create_object(element, api_token, type=type) for element in data]
    elif isinstance(data, dict) and not isinstance(data, AXSemanticsObject):
        data = data.copy()

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
        self.base = api_base or constants.API_BASE
        self.token = token

    def request(self, method, call_url, params, user_headers=None):
        url = '{}{}/'.format(self.base, call_url)
        token = self.token or constants.API_TOKEN

        if method == 'get' or method == 'delete':
            if params:
                url += self.encode_params(params)

        headers = {
            'User-Agent': 'AXSemantics Python Client',
            'Content-Type': 'application/json',
        }

        if token:
            headers.update({'Authorization': 'Token {}'.format(token)})

        if user_headers:
            headers.update(user_headers)

        if method == 'post':
            result = requests.post(method, url, headers=headers, json=params)
        else:
            result = requests.request(method, url, headers=headers)

        if result.status_code == 200 or result.status_code == 201:
            return result.json()
        else:
            return result

    def encode_params(self, params):
        if isinstance(params, dict):
            return '?' + self._dict_encode(params)
        if isinstance(params, list):
            return '?' + '&'.join(self._dict_encode(d) for d in params)

    def _dict_encode(self, data):
        result = []
        for key, value in data.items():
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
    def create_from_dict(cls, data, api_token=None):
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

        for key, value in data.items():
            super().__setitem__(key, create_object(value, api_token))

        self._previous = data

    def request(self, method, url, params=None, headers=None):
        params = params or self._params
        requestor = RequestHandler(token=self.api_token, api_base=self.api_base)
        response = requestor.request(method, url, params, headers)
        return create_object(response, self.api_token)

    def serialize(self, previous):
        params = {}
        unsaved_keys = self._unsaved_attributes or set()
        previous = previous or self._previous or {}

        for key, value in self.items():
            if key == 'id' or (isinstance(key, str) and key.startswith('_')) or isinstance(value, APIResource):
                continue
            elif hasattr(value, 'serialize'):
                params[key] = value.serialize(previous.get(key, None))
            elif key in unsaved_keys:
                params[key] = _get_update_dict(value, previous.get(key, None))

        return params


class APIResource(AXSemanticsObject):
    @classmethod
    def retrieve(cls, id, api_token=None, **kwargs):
        instance = cls(id, api_token, **kwargs)
        instance.refresh()
        return instance

    def refresh(self):
        self.load_data(self.request('get', self.instance_url()))
        return self

    @classmethod
    def class_name(cls):
        return str(requests.utils.quote(cls.__name__.lower()))

    @classmethod
    def class_url(cls):
        return '/v1/{}'.format(cls.class_name)

    def instance_url(self):
        id = self.get('id')
        return '{}/{}'.format(self.class_url(), requests.utils.quote(str(id)))


class ListResource(APIResource):
    @property
    def initial_url(self):
        pass

    def __init__(self, api_token=None):
        self.current_index = None
        self.current_list = None
        self.next_page = 1
        self._params = None
        self.length = 0
        object.__setattr__(self, 'api_token', api_token)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_list == None:
            self._update()

        if self.current_index >= len(self.current_list):
            if self.next_page:
                self._update()
            else:
                raise StopIteration
        self.current_index += 1
        return create_object(self.current_list[self.current_index - 1], api_token=self.api_token)

    def __len__(self):
        return self.length

    def _update(self, params=None):
        if self.next_page > 1:
            params = {'page': self.next_page}

        r = self.request('get', self.initial_url, params=params)

        self.current_index = 0
        self.length = r['count']
        self.current_list = r['results']

        if r['next']:
            self.next_page += 1
        else:
            self.next_page = None


class CreateableResourceMixin:
    @classmethod
    def create(cls, api_token=None, api_base=None, **params):
        requestor = RequestHandler(token=api_token)
        response = requestor.request('post', cls.class_url(), params)
        return create_object(response, api_token)


class UpdateableResourceMixin:
    def save(self):
        params = self.serialize(None)
        self.load_data(self.request('post', self.instance_url(), params))
        return self


class DeleteableResourceMixin:
    def delete(self, params=None):
        self.load_data(self.request('delete', self.instance_url(), params))
        return self


class ContentProject(CreateableResourceMixin, DeleteableResourceMixin, APIResource):
    class_name = 'content-project'

    def __init__(self, *args, **kwargs):
        super(ContentProject, self).__init__(*args, **kwargs)
        thing_list = ThingList(cp_id=self.id, api_token=self.api_token)
        object.__setattr__(self, 'things', thing_list)


class ContentProjectList(ListResource):
    initial_url = ContentProject.class_url()


class ThingList(ListResource):

    def __init__(self, cp_id, *args, **kwargs):
        super(ThingList, self).__init__(*args, **kwargs)
        self.cp_id = cp_id

    @property
    def initial_url(self):
        return '{}/{}/thing'.format(ContentProject.class_url(), self.cp_id)


class Thing:
    pass
