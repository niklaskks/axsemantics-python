import os

from pytest_bdd import (
    scenario,
    given, when, then,
    parsers,
)

from models.content_project import ContentProject


@scenario('../features/upload.feature', 'Excel file upload')
def test_excel_file_upload():
    # maybe set up mock here for acceptance tests
    pass


@given(parsers.parse('I have a file "{file_name}"'))
def local_file(file_name):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', file_name)
    return os.path.abspath(file_path)


@given(parsers.parse('I have the API token "{api_token}"'))
def token(api_token):
    return api_token


@given(parsers.parse('I have a content project for "{thing_type}"'))
def tv_content_project(thing_type, token):
    # check method name and signature: are those parameters correct and enough?
    # think hard about high-level interface here
    return ContentProject(88)


@when('I upload the file')
def upload_into_content_project(local_file, tv_content_project):
    # the http call to the api needs to be mocked for this
    # also update content project fixture with mocked data
    tv_content_project.bulk_upload(local_file)


@then('I want to see the data in the content project')
def is_all_the_data_in_content_project(tv_content_project):
    thing_list = list(tv_content_project.things())
    assert len(thing_list) == 3
