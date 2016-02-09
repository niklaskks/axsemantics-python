def create_object(data, api_token):
    types = {
        'contentproject': ContentProject,
        'thing': Thing,
    }

    if isinstance(data, list):
        return [create_object(element, api_token) for element in data]
    elif isinstance(data, dict):
        data = data.copy()
        class_name = data.get('type')
        id = data.get('id')
        _class = types.get('type', AXSemanticsObject)
        return _class.create_from_dict(data, id, api_token)
    else:
        return data


class AXSemanticsObject(dict):
    def __init__(self, id, atokenkey=None, **kwargs):
        super(AXSemanticsObject, self)
        self._unsaved = set()
        self['id'] = id
        self['api_token'] = atokenkey

    def update(self, update_dict):
        for key in update_dict:
            self._unsaved.add(key)
        return super(AXSemanticsObject, self).update(update_dict)

    def __setitem__(self, key, value):
        self._unsaved.add(key)
        return super(AXSemanticsObject, self).__setitem__(key, value)

    def __delitem__(self, key):
        self._unsaved.remove(key)
        return super(AXSemanticsObject, self).__delitem__(key)

    @classmethod
    def create_from_dict(cls, data, api_token):
        instance = cls(data.get('id')), api_token=api_token)
        instance.load(data, api_token=api_token)
        return instance

    def load(self, data, api_token=None, partial=False):
        self.api_token = api_token or getattr(data, 'api_token', None)

        if partial:
            self._unsaved -= set(data)
        else:
            self._unsaved = set()
            self.clear()

        for key, value in data.iteritems():
            self[key] = create_object(value, api_token)

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
