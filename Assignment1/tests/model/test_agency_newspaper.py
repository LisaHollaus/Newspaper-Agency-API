import pytest

from ...src.model.newspaper import Newspaper
from ..fixtures import app, client, agency


# adding and getting all newspapers:
def test_add_newspaper(agency):
    before = len(agency.newspapers)
    new_paper = Newspaper(paper_id=999,
                          name="Sim Comic",
                          frequency=7,
                          price=3.14)
    agency.add_newspaper(new_paper)
    assert len(agency.all_newspapers()) == before + 1


def test_add_newspaper_same_id_should_raise_error(agency):
    before = len(agency.newspapers)
    new_paper = Newspaper(paper_id=99,
                          name="Simpsons Comic",
                          frequency=7,
                          price=3.14)
    # first adding of newspaper should be okay
    agency.add_newspaper(new_paper)
    new_paper2 = Newspaper(paper_id=99,
                           name="Superman Comic",
                           frequency=7,
                           price=13.14)
    with pytest.raises(ValueError, match='A newspaper with ID 99 already exists'):  # <-- this allows us to test for exceptions
        # this one should raise an exception!
        agency.add_newspaper(new_paper2)
    assert len(agency.all_newspapers()) == before + 1  # make sure only 1 newspaper got added to the list


def test_add_newspaper_existing_paper_should_raise_error(agency):
    before = len(agency.newspapers)
    new_paper = Newspaper(paper_id=199,
                          name="Comics",
                          frequency=7,
                          price=13.14)
    # first adding of newspaper should be okay
    agency.add_newspaper(new_paper)
    new_paper2 = Newspaper(paper_id=5,
                           name="Comics",
                           frequency=7,
                           price=13.14)
    with pytest.raises(ValueError, match='Newspaper named Comics already exists'):  # <-- this allows us to test for exceptions
        # this one should raise an exception!
        agency.add_newspaper(new_paper2)
    assert len(agency.all_newspapers()) == before + 1  # make sure only 1 newspaper got added to the list


# getting a newspaper by ID:
def test_get_newspaper_by_id(agency):
    paper_id = 12222
    name = "New York times"
    frequency = 10
    price = 15.00
    new_paper = Newspaper(paper_id=paper_id,
                          name=name,
                          frequency=frequency,
                          price=price)
    agency.add_newspaper(new_paper)
    get_paper = agency.get_newspaper(paper_id)
    assert get_paper.paper_id == paper_id
    assert get_paper.name == name
    assert get_paper.frequency == frequency
    assert get_paper.price == price


# remove a newspaper:
def test_remove_newspaper(agency):
    before = len(agency.newspapers)
    new_paper = Newspaper(paper_id=500,
                          name="Hollywood",
                          frequency=12,
                          price=20.50)
    agency.add_newspaper(new_paper)
    assert len(agency.all_newspapers()) == before + 1
    agency.remove_newspaper(new_paper)
    assert len(agency.all_newspapers()) == before


# update newspaper:
def test_update_newspaper(agency, app):
    with app.app_context():
        old_paper = agency.get_newspaper(100)  # using testdata
        paper_id = old_paper.paper_id
        name = "Updated"
        frequency = 70
        price = 20.00
        updated_paper = Newspaper(paper_id=paper_id,
                                  name=name,
                                  frequency=frequency,
                                  price=price)
        agency.update_newspaper(old_paper, updated_paper)
        get_paper = agency.get_newspaper(paper_id)
        assert old_paper != updated_paper and old_paper != get_paper
        assert updated_paper == get_paper
        assert get_paper.paper_id == paper_id
        # making sure the paper keeps its issues and subscribers:
        assert get_paper.issues == updated_paper.issues
        assert get_paper.subscribers == updated_paper.subscribers
        with pytest.raises(ValueError, match='Newspaper already up to date'):
            # updating newspaper without a change should raise an exception!
            agency.update_newspaper(updated_paper, updated_paper)
