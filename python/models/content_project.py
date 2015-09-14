# coding=utf-8
from decimal import Decimal
from io import FileIO
import os

import durga


class FileEmptyError(FileExistsError):
    pass


class ContentProject(durga.Resource):

    base_url = 'http://localhost:9000/v1'
    path = 'content-project'
    objects_path = ('results',)
    headers = {
        'Authorization': 'Token 851843132acb0ca11dc022ce480eea6939c76efb',
    }

    schema = durga.schema.Schema({
        'id': durga.schema.Use(int),
        'name': durga.schema.Use(str),
        'keyword_deviation': durga.schema.Use(Decimal),
        'keyword_density': durga.schema.Use(Decimal),
        'max_length': durga.schema.Use(int),
        'min_length': durga.schema.Or(int, None),
        'engine_configuration': durga.schema.Use(int),  # resolve to EngineConfiguration
        'axcompany': durga.schema.Use(int),
        'axcompany_name': durga.schema.Use(str),
        'count_generated_texts': durga.schema.Use(int),
        'count_generated_texts_errors': durga.schema.Use(int),
        'count_things': durga.schema.Use(int),
    })

    def bulk_upload(self, local_file: str):

        if not isinstance(local_file, str):
            raise FileNotFoundError('Argument `local_file` must be "str"; found "{}"'.format(type(local_file)))

        if os.path.getsize(local_file) == 0:
            raise FileEmptyError('Argument `local_file` must not be an empty file.')

    def things(self):
        return []
