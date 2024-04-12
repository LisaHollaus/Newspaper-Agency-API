import pytest

from ...src.model.subscriber import Subscriber
from ...src.model.issue import Issue
from ..fixtures import app, client, agency


# adding and getting all subscriber:
def test_add_subscriber(agency):
    before = len(agency.subscribers)
    new_subscriber = Subscriber(ID=111,
                                name="Jim",
                                address="Flowerstreet 12")
    agency.add_subscriber(new_subscriber)
    assert len(agency.all_subscribers()) == before + 1


def test_add_subscriber_same_id_should_raise_error(agency):
    before = len(agency.subscribers)
    new_subscriber = Subscriber(ID=115,
                                name="James",
                                address="Blossomavenue 16")
    agency.add_subscriber(new_subscriber)
    new_subscriber2 = Subscriber(ID=115,
                                 name="Jim",
                                 address="Sunstreet 12")
    with pytest.raises(ValueError, match='A subscriber with ID 115 already exists'):
        # this one should rais ean exception!
        agency.add_subscriber(new_subscriber2)
    assert len(agency.all_subscribers()) == before + 1  # make sure only 1 subscriber got added to the list


def test_add_subscriber_same_person_should_raise_error(agency):
    before = len(agency.subscribers)
    new_subscriber = Subscriber(ID=1,
                                name="Joe",
                                address="Flowerstreet 12")
    agency.add_subscriber(new_subscriber)
    new_subscriber2 = Subscriber(ID=3,
                                 name="Joe",
                                 address="Flowerstreet 12")
    with pytest.raises(ValueError, match='Subscriber Joe already exists'):
        # this one should rais ean exception!
        agency.add_subscriber(new_subscriber2)
    assert len(agency.all_subscribers()) == before + 1  # make sure only 1 subscriber got added to the list


# getting a subscriber by ID:
def test_get_subscriber_by_id(agency):
    ID = 12222
    name = "Tony"
    address = "Starktower 1"
    new_subscriber = Subscriber(ID=ID,
                                name=name,
                                address=address)
    agency.add_subscriber(new_subscriber)
    get_subscriber = agency.get_subscriber(ID)
    assert get_subscriber.ID == ID
    assert get_subscriber.name == name
    assert get_subscriber.address == address


# remove a subscriber:
def test_remove_subscriber(agency):
    before = len(agency.subscribers)
    new_subscriber = Subscriber(ID=1000,
                                name="Otto",
                                address="Ottohausen 5")
    agency.add_subscriber(new_subscriber)
    assert len(agency.all_subscribers()) == before + 1
    agency.remove_subscriber(new_subscriber)
    assert len(agency.all_subscribers()) == before


# update subscriber:
def test_update_subscriber(agency, app):
    with app.app_context():
        old_subscriber = agency.get_subscriber(10)  # using testdata
        ID = old_subscriber.ID
        name = "another name"
        address = "somewhere else"
        updated_subscriber = Subscriber(ID=ID,
                                        name=name,
                                        address=address)
        agency.update_subscriber(old_subscriber, updated_subscriber)
        get_subscriber = agency.get_subscriber(ID)
        assert old_subscriber != updated_subscriber
        assert updated_subscriber == get_subscriber
        assert get_subscriber.ID == ID
        # making sure the subscriber keeps its issues and newspapers:
        assert get_subscriber.issues_list == updated_subscriber.issues_list
        assert get_subscriber.newspaper_list == updated_subscriber.newspaper_list
        with pytest.raises(ValueError, match="No changes made"):  # updating editor without a change
            # this one should raise an exception!
            agency.update_editor(updated_subscriber, updated_subscriber)


# subscribe to newspaper (unsubscribe when subscriber gets deleted):
def test_subscribe_to_paper(agency, app):
    # add subscriptions
    with app.app_context():
        subscriber = agency.get_subscriber(103)
        paper = agency.get_newspaper(115)
        agency.subscribe_to_paper(subscriber, paper)
        assert subscriber in paper.subscribers
        assert paper in subscriber.newspaper_list
        with pytest.raises(ValueError, match=f"Subscriber {subscriber.ID} already has a subscription of the Newspaper {paper.name}"):
            # subscribing a second time should raise an exception!
            agency.subscribe_to_paper(subscriber, paper)

        # unsubscribe, by deleting the subscriber
        agency.remove_subscriber(subscriber)
        # check if all subscriptions got cancelled:
        for p in agency.newspapers:
            assert subscriber not in p.subscribers
        assert subscriber not in paper.subscribers


# check for missing issues
def test_check_missingissues(agency, app):
    with app.app_context():
        # arrange
        subscriber = agency.get_subscriber(150)
        paper = agency.get_newspaper(115)
        agency.subscribe_to_paper(subscriber, paper)
        new_issue = Issue(issue_id=2,
                          releasedate=2025-11-13,
                          released=False,  # Initially, paper issues are not published
                          editor_id=1,  # exists in testdata
                          pages=12)
        agency.add_issue(paper, new_issue)
        agency.release_issue(new_issue)

        # act
        before = agency.check_missingissues(subscriber)
        assert before == "Undelivered Issues from: ['Wall Street Journal: Issues with ID 2 ']"
        agency.deliver_issue(subscriber, new_issue, paper)
        assert before != len(agency.check_missingissues(subscriber))
        assert agency.check_missingissues(subscriber) == "Undelivered Issues from: []"
