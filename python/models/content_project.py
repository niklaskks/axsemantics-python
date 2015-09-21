# coding=utf-8
from decimal import Decimal
import os
import uuid

from dateutil import parser as dateparser
import durga


class FileEmptyError(FileExistsError):
    pass


class MyaxResource(durga.Resource):
    headers = {
        'Authorization': 'Token 851843132acb0ca11dc022ce480eea6939c76efb',
    }
    base_url = 'http://localhost:9000/v1'


class ContentProjectResource(MyaxResource):
    path = 'content-project'
    id_attribute = 'id'
    objects_path = ('results',)

    schema = durga.schema.Schema({
        'id': int,
        'name': str,
        'keyword_deviation': Decimal,
        'keyword_density': Decimal,
        'max_length': int,
        'min_length': durga.schema.Optional(int),
        'engine_configuration': int,  # resolve to EngineConfiguration
        'axcompany': int,
        'axcompany_name': str,
        'count_generated_texts': int,
        'count_generated_texts_errors': int,
        'count_things': int,
    })


class ThingListResource(MyaxResource):
    path = 'content-project/{id}/thinglist'
    path_params = ('id',)
    objects_path = ('results',)

    schema = durga.schema.Schema({
        'id': int,
        'tag': str,
        'name': str,
        'sku': str,
        'requirement_level_status_text': str,
        'axcompany_pk': int,
        'modified': durga.schema.Use(dateparser.parse),  # '2015-07-23T12:53:09.008947+00:00',
        'status': str,
        'thing_type': str,
        'uid': str,
        'uuid': durga.schema.Use(lambda n: uuid.UUID(n, version=4)),  # '4d6a8f72-293f-48c1-8a3c-51e1ef9d7249',
        'content_project_pk': int,
        'most_important_missing_requirement_level': int,
        'metrics.text_length_in_chars': durga.schema.Optional(str),
        'metrics.text_length_in_words': durga.schema.Optional(int),
    })


class BulkUploadResource(durga.Resource):
    path = 'bulk-upload'
    objects_path = ('results',)

    schema = durga.schema.Schema({
        'data_file': open,
        'content_project': str,
        'tag': durga.schema.Optional(str),
    })


class ContentProject:
    backend = ContentProjectResource

    def __init__(self, pk):
        self.pk = pk

    def bulk_upload(self, local_file: str):
        """
        Uploads given file to this content project.

        Internally, uploading is delegated to BulkUpload model.

        :param local_file: path to file that will be uploaded
        :return:
        """

        BulkUpload.upload_file(local_file=local_file, content_project=self)

    def things(self):
        return [1, 2, 3]
        # return ThingList().collection.get(id=self.id)


class ThingList:

    backend = ThingListResource

    def __init__(self, content_project: ContentProjectResource):
        self.content_project = content_project


class BulkUpload:
    backend = BulkUploadResource

    @staticmethod
    def upload_file(local_file: str, content_project: ContentProject):

        if not isinstance(local_file, str):
            raise FileNotFoundError('Argument `local_file` must be "str"; found "{}"'.format(type(local_file)))

        if os.path.getsize(local_file) == 0:
            raise FileEmptyError('Argument `local_file` must not be an empty file.')

        cp_id = content_project.pk
