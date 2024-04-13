
import pytest

from ..src.app import create_app
from ..src.model.agency import Agency
from .testdata import populate, populate_issues


@pytest.fixture()
def app():
    yield create_app()


@pytest.fixture()
def client(app):
    yield app.test_client()


@pytest.fixture()
def agency(app):
    agency = Agency.get_instance()
    populate(agency)
    populate_issues(agency.newspapers[0])  # add issues to the first newspaper in the list (ID 100)
    yield agency

