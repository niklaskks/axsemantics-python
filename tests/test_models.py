# coding=utf-8

from inspect import signature

import pytest


# noinspection PyShadowingNames,PyMethodMayBeStatic,PyUnresolvedReferences
class TestContentProject:
    def test_has_attribute_bulk_upload(self, content_project):
        assert hasattr(content_project, 'bulk_upload')

    def test_has_attribute_generate_content(self, content_project):
        assert hasattr(content_project, 'generate_content')

    def test_generate_content_is_callable(self, content_project):
        assert callable(content_project.generate_content)

    def test_generate_content_accepts_argument(self, content_project):
        sig = signature(content_project.generate_content)

        assert len(list(sig.parameters)) >= 1
        assert 'force' in sig.parameters

    @pytest.mark.parametrize('force', [True, False])
    def test_generate_content_returns_int(self, content_project, force):
        rvalue = content_project.generate_content(force=force)
        assert isinstance(rvalue, int)

    def test_has_attribute_things(self, content_project):
        assert hasattr(content_project, 'things')

    def test_upload_attribute_is_callable(self, content_project):
        assert callable(content_project.bulk_upload)

    def test_upload_method_accepts_argument(self, content_project):
        sig = signature(content_project.bulk_upload)

        assert len(list(sig.parameters)) > 0  # apparently, 'self' does not count

    def test_upload_method_returns_none(self, content_project, test_tv_file):
        rtype = content_project.bulk_upload(test_tv_file)
        assert rtype is None

    @pytest.mark.parametrize('file_name', [
        'should_not_exi.st',
        '',
        None,
    ])
    def test_upload_method_raises_error_on_invalid_file_name(self, content_project, file_name):
        with pytest.raises(FileNotFoundError):
            content_project.bulk_upload(file_name)

    def test_upload_method_raises_error_on_empty_file(self, content_project, empty_file):
        from models.content_project import FileEmptyError

        with pytest.raises(FileEmptyError):
            content_project.bulk_upload(empty_file)
