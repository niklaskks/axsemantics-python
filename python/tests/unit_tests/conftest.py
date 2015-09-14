# coding=utf-8
import os

import pytest


@pytest.fixture(scope='session')
def content_project() -> 'ContentProject':
    from models.content_project import ContentProject
    # todo mock http traffic with httpretty
    return ContentProject()


@pytest.fixture(scope='session')
def empty_file() -> str:
    """
    Returns a complete absolute path to an empty Excel file.
    """
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'empty_file.xlsx')

    return os.path.abspath(file_path)
