from axsemantics import constants
from axsemantics.base import (
    APIResource,
    ListResource,
)
from axsemantics.mixins import(
    ContentGenerationMixin,
    CreateableMixin,
    DeleteableMixin,
    ListableMixin,
    UpdateableMixin,
)
from axsemantics.utils import create_object


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


class Thing(CreateableMixin, UpdateableMixin, DeleteableMixin, ListableMixin, ContentGenerationMixin, APIResource):
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


class ContentProject(CreateableMixin, DeleteableMixin, ListableMixin, ContentGenerationMixin, APIResource):
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
