import json

from axsemantics.base import ListResource


class CreateableMixin:
    def create(self, api_token=None, api_base=None, **params):
        params = {key: self[key] for key in self.required_fields}
        params.update(self.serialize(None))
        self.load_data(self.request('post', self.instance_url(), params=params))
        return self


class UpdateableMixin:
    @property
    def required_fields(self):
        return []

    def __init__(self, *args, **kwargs):
        super(UpdateableMixin, self).__init__(*args, **kwargs)
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


class DeleteableMixin:
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
