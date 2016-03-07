import json

import requests

from axsemantics import constants
from axsemantics.errors import (
    APIConnectionError,
    APIError,
    AuthenticationError,
)


def login(user, password, api_base=None):
    data = {
        'email': user,
        'password': password,
    }
    requestor = RequestHandler()

    try:
        response = requestor.request(
            url='/{}/rest-auth/login/'.format(constants.API_VERSION),
            method='post',
            params=data,
        )
    except APIError as error:
        if hasattr(error, 'request') and error.request.status_code == 400:
            raise AuthenticationError(error.request) from None
        else:
            raise

    if constants.DEBUG:
        print('Received authentication token {}.'.format(response['key']))
    constants.API_TOKEN = response['key']


def create_object(data, api_token=None, _type=None, **kwargs):
    types = {
        'content-project': ContentProject,
        'thing': Thing,
    }

    if isinstance(data, list):
        return [create_object(element, api_token, type=_type, **kwargs) for element in data]

    if isinstance(data, dict) and not isinstance(data, AXSemanticsObject):
        data = data.copy()

        _class = types.get(_type, AXSemanticsObject)
        return _class.create_from_dict(data, api_token, **kwargs)

    return data


def _get_update_dict(current, previous):
    if isinstance(current, dict):
        previous = previous or {}
        diff = current.copy()
        diff.update({
            key: ''
            for key in set(previous.keys()) - set(current.keys())
        })
        return diff

    return current if current is not None else ""


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


class AXSemanticsObject(dict):
    class_name = 'AXSemanticsObject'

    def __init__(self, api_token=None, api_base=None, **kwargs):
        super(AXSemanticsObject, self).__init__()
        self._unsaved_attributes = set()
        self._params = kwargs
        self._previous = None
        self.api_base = api_base or constants.API_BASE

        self['id'] = kwargs.get('id', None)
        object.__setattr__(self, 'api_token', api_token)

    def update(self, update_dict):
        for key in update_dict:
            self._unsaved_attributes.add(key)
        return super(AXSemanticsObject, self).update(update_dict)

    def __setitem__(self, key, value):
        self._unsaved_attributes.add(key)
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        self._unsaved_attributes.remove(key)
        return super(AXSemanticsObject, self).__delitem__(key)

    @classmethod
    def create_from_dict(cls, data, api_token=None, **kwargs):
        instance = cls(api_token=api_token, **kwargs)
        instance.load_data(data, api_token=api_token)
        return instance

    def load_data(self, data, api_token=None, partial=False):
        self.api_token = api_token or getattr(data, 'api_token', None)

        if partial:
            self._unsaved_attributes -= set(data)
        else:
            self._unsaved_attributes = set()
            self.clear()

        if data:
            for key, value in data.items():
                super().__setitem__(key, create_object(value, api_token, _type=self.class_name))

        self._previous = data

    def request(self, method, url, params=None, headers=None):
        params = params or self._params
        requestor = RequestHandler(
            token=self.api_token,
            api_base=self.api_base or constants.API_BASE,
        )
        response = requestor.request(method, url, params, headers)
        return create_object(response, self.api_token, _type=self.class_name)

    def serialize(self, previous):
        params = {}
        unsaved_keys = self._unsaved_attributes or set()
        previous = previous or self._previous or {}

        for key, value in self.items():
            if key == 'id' or (isinstance(key, str) and key.startswith('_')) or isinstance(value, APIResource):
                continue
            if hasattr(value, 'serialize'):
                params[key] = value.serialize(previous.get(key, None))
            elif key in unsaved_keys:
                params[key] = _get_update_dict(value, previous.get(key, None))

        return params


class APIResource(AXSemanticsObject):
    @classmethod
    def retrieve(cls, id, api_token=None, **kwargs):
        instance = cls(api_token, id=id, **kwargs)
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
        return '/{}/{}/'.format(constants.API_VERSION, cls.class_name)

    def instance_url(self):
        if self.get('id', None):
            id = self['id']
            return '{}{}/'.format(self.class_url(), requests.utils.quote(str(id)))
        else:
            return self.class_url()


class ListResource:
    def __init__(self, class_name, initial_url, api_token=None, api_base=None):
        self.current_index = None
        self.current_list = None
        self.next_page = 1
        self._params = None
        self.length = 0
        self.api_base = api_base or constants.API_BASE
        self.api_token = api_token or constants.API_TOKEN
        self.class_name = class_name
        self.initial_url = initial_url
        self._update()

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_index >= len(self.current_list):
            if self.next_page:
                self._update()
            else:
                raise StopIteration
        self.current_index += 1
        return create_object(self.current_list[self.current_index - 1], api_token=self.api_token, _type=self.class_name)

    def __len__(self):
        return self.length

    def __repr__(self):
        return 'List of {} objects of type "{}"'.format(len(self), self.class_name)

    def _update(self, params=None):
        if self.next_page > 1:
            params = {'page': self.next_page}

        requestor = RequestHandler(token=self.api_token)
        response = requestor.request('get', self.initial_url, params)

        self.current_index = 0
        self.length = response['count']
        self.current_list = response['results']

        if response['next']:
            self.next_page += 1
        else:
            self.next_page = None

    def get(self, **kwargs):
        for item in self:
            if all([item[key] == kwargs[key] for key in kwargs]):
                return item
        return None


class CreateableResourceMixin:
    def create(self, api_token=None, api_base=None, **params):
        params = {key: self[key] for key in self.required_fields}
        params.update(self.serialize(None))
        self.load_data(self.request('post', self.instance_url(), params=params))
        return self


class UpdateableResourceMixin:
    @property
    def required_fields(self):
        return []

    def __init__(self, *args, **kwargs):
        super(UpdateableResourceMixin, self).__init__(*args, **kwargs)
        for key in self.required_fields:
            if key in kwargs:
                self[key] = kwargs[key]
            else:
                self[key] = None

    def save(self):
        # these would be the params for PATCH
        # params = {key: self[key] for key in self.required_fields}
        # params.update(self.serialize(None))
        params = json.dumps(self)
        self.load_data(self.request('put', self.instance_url(), params))
        return self


class DeleteableResourceMixin:
    def delete(self, params=None):
        self.load_data(self.request('delete', self.instance_url(), params))
        return self


class ListableMixin:
    list_class = None

    @classmethod
    def all(cls):
        if not cls.list_class:
            return ListResource(initial_url=cls.class_url(), class_name=cls.class_name)
        return cls.list_class


class ContentGenerationMixin:
    def generate_content(self, force=False, params=None):
        url = '{}generate_content/?force={}'.format(self.instance_url(), str(force).lower())
        return self.request('post', url, params)


class ContentProject(CreateableResourceMixin, DeleteableResourceMixin, ListableMixin, ContentGenerationMixin, APIResource):
    class_name = 'content-project'
    required_fields = ['name', 'engine_configuration']

    def __init__(self, api_token=None, **kwargs):
        super(ContentProject, self).__init__(api_token=api_token, **kwargs)

    def things(self):
        if self['id']:
            thing_url = '{}thing/'.format(self.instance_url())
            return ThingList(cp_id=self['id'], api_token=self.api_token, class_name=self.class_name, initial_url=thing_url)


class ContentProjectList(ListResource):
    initial_url = ContentProject.class_url()
    class_name = 'content-project'


class ThingList(ListResource):
    class_name = 'thing'

    def __init__(self, cp_id, *args, **kwargs):
        self.cp_id = cp_id
        super(ThingList, self).__init__(*args, **kwargs)

    def __next__(self):
        if self.current_index >= len(self.current_list):
            if self.next_page:
                self._update()
            else:
                raise StopIteration
        self.current_index += 1
        return create_object(self.current_list[self.current_index - 1], api_token=self.api_token, _type=self.class_name, cp_id=self.cp_id)


class Thing(CreateableResourceMixin, UpdateableResourceMixin, DeleteableResourceMixin, ListableMixin, ContentGenerationMixin, APIResource):
    class_name = 'thing'
    required_fields = ['uid', 'name', 'content_project']
    list_class = ThingList

    def __init__(self, cp_id=None, **kwargs):
        super(Thing, self).__init__(**kwargs)
        self['content_project'] = cp_id

    def instance_url(self):
        url = '/{}/content-project/{}/thing/'.format(
            constants.API_VERSION,
            self['content_project'],
        )
        if self['id']:
            url += '{}/'.format(self['id'])
        return url
