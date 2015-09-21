# coding=utf-8
import os

import pytest

HERE = os.path.dirname(__file__)


@pytest.fixture(scope='session')
def content_project() -> 'ContentProject':
    from models.content_project import ContentProject
    # todo mock http traffic with httpretty
    return ContentProject(80)


@pytest.fixture(scope='session')
def empty_file() -> str:
    """
    Returns a complete absolute path to an empty Excel file.
    """
    file_path = path_to('empty_file.xlsx')

    return os.path.abspath(file_path)


@pytest.fixture(scope='session')
def test_tv_file() -> str:
    """
    Returns a complete absolute path to a working data file that contains 3 TV
    things.
    """

    file_path = path_to('test_tv.xlsx')

    return os.path.abspath(file_path)


def path_to(file_name):
    file_path = os.path.join(HERE, '..', 'data', file_name)
    return file_path
