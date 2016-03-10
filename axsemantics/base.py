import requests

from axsemantics import constants
from axsemantics.net import RequestHandler
from axsemantics.utils import (
    create_object,
    _get_update_dict,
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
