# import the fixtures (this is necessary!)
from ..fixtures import app, client, agency


def test_get_subscriber_should_list_all_subscribers(client, agency):
    # send request
    response = client.get("/subscriber/")   # <-- note the slash at the end!

    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    assert len(parsed["subscriber"]) == len(agency.subscribers)


def test_post_add_subscriber(client, agency):
    # arrange
    subscriber_count_before = len(agency.subscribers)

    # act
    response = client.post("/subscriber/",
                           json={
                               "ID": 600,
                               "name": "Maximilian",
                               "address": "Weidenaurotte 2"
                           })
    # test status code
    assert response.status_code == 200

    # verify
    assert len(agency.subscribers) == subscriber_count_before + 1

    # parse response and check that the correct data is here
    parsed = response.get_json()
    subscriber_response = parsed["subscriber"]
    assert subscriber_response["ID"] == 600
    assert subscriber_response["name"] == "Maximilian"
    assert subscriber_response["address"] == "Weidenaurotte 2"


def test_get_subscriber_should_list_specific_subscriber(client, agency):
    # send request
    response = client.get("/subscriber/10")   # using testdata

    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    paper_response = parsed["subscriber"]
    assert paper_response["ID"] == 10


def test_post_update_subscriber(client, agency):
    # act
    response = client.post("/subscriber/150",  # using testdata
                           json={
                               "name": "Emilia",
                               "address": "Churchstreet 5"
                           })
    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    paper_response = parsed["subscriber"]
    assert paper_response["ID"] == 150
    assert paper_response["name"] == "Emilia"
    assert paper_response["address"] == "Churchstreet 5"


def test_post_update_subscriber_with_invalid_ID(client, agency):
    # act
    response = client.post("/subscriber/65500",
                           json={
                               "name": "Emilia",
                               "address": "Churchstreet 5"
                           })
    # test status code
    assert response.status_code == 404  # not found


def test_delete_subscriber(client, agency):
    # prepare
    old_subscriber_list = len(agency.subscribers)
    # send request
    response = client.delete("/subscriber/120")

    # test status code
    assert response.status_code == 200

    # test if subscriber got deleted from the list
    new_subscriber_list = len(agency.subscribers)
    assert new_subscriber_list == old_subscriber_list - 1


def test_post_subscribe_to_a_newspaper(client, agency):
    # prepare
    paper = agency.get_newspaper(100)
    subscriber_list = len(paper.subscribers)

    # act (using testdata)
    response = client.post("/subscriber/160/subscribe",
                           json={
                               "paper_id": 100
                           })
    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    assert parsed == "Done!"
    assert subscriber_list + 1 == len(paper.subscribers)  # making sure the subscriber got added to the list


def test_post_subscribe_to_a_newspaper_with_unknown_subscriber(client, agency):
    # prepare
    paper = agency.get_newspaper(100)
    subscriber_list = len(paper.subscribers)

    # act (using testdata)
    response = client.post("/subscriber/2323/subscribe",
                           json={
                               "paper_id": 100
                           })
    # test status code
    assert response.status_code == 404  # not found
    # assert that the subscriber did not get added to the list
    assert subscriber_list == len(paper.subscribers)


def test_post_subscribe_to_a_newspaper_with_unknown_newspaper(client, agency):
    # prepare
    paper = agency.get_newspaper(100)
    subscriber_list = len(paper.subscribers)

    # act (using testdata)
    response = client.post("/subscriber/150/subscribe",
                           json={
                               "paper_id": 5100
                           })
    # test status code
    assert response.status_code == 404  # not found
    # assert that the subscriber did not get added to the list
    assert subscriber_list == len(paper.subscribers)


def test_get_subscriber_stats(client, agency, app):
    with app.app_context():
        # prepare
        # deliver issue with subscription
        paper = agency.get_newspaper(100)
        subscriber = agency.get_subscriber(10)
        issue = agency.get_issue(paper, 90)
        agency.subscribe_to_paper(subscriber, paper)
        agency.release_issue(issue)

        res = client.post("/newspaper/100/issue/90/deliver",
                          json={
                              "ID": 10
                          })
        assert res.status_code == 200

        # deliver issue without subscription (special issue)
        paper2 = agency.get_newspaper(101)
        response = client.post("/newspaper/101/issue",  # creating a new issue
                               json={
                                   "issue_id": 1,
                                   "releasedate": "2025-12-17",
                                   "released": False,
                                   "editor_id": 102,
                                   "pages": 70
                               })
        assert response.status_code == 200
        new_issue = agency.get_issue(paper2, 1)
        agency.release_issue(new_issue)
        res = client.post("/newspaper/101/issue/1/deliver",  # special issue
                          json={
                              "ID": 10
                          })
        assert res.status_code == 200
        # send request
        response = client.get("/subscriber/10/stats")

        # test status code
        assert response.status_code == 200

        parsed = response.get_json()
        assert parsed == ("Number of newspaper subscriptions: 1 "
                          "Cost: 13.14 monthly or 157.68 annually "
                          "Number of Issues received from: ['The New York Times: 1'] "
                          "Special issues without subscription: Issue with ID 1 from 'Heute', ")


def test_get_subscriber_stats_with_unknown_subscriber(client, agency):
    # send request
    response = client.get("/subscriber/43/stats")

    # test status code
    assert response.status_code == 404  # not found


def test_get_check_missingissues(client, agency, app):
    with app.app_context():
        # arrange
        paper = agency.get_newspaper(135)
        subscriber = agency.get_subscriber(170)
        agency.subscribe_to_paper(subscriber, paper)

        # creating a new issue instead of using the testdata, because it would interfere too much with other tests
        response = client.post("/newspaper/135/issue",
                               json={
                                   "issue_id": 1,
                                   "releasedate": "2025-12-15",
                                   "released": False,
                                   "editor_id": 1,
                                   "pages": 13
                                    })
        assert response.status_code == 200
        issue = agency.get_issue(paper, 1)
        agency.release_issue(issue)

        # send request
        response = client.get("/subscriber/170/missingissues")

        # test status code
        assert response.status_code == 200

        parsed = response.get_json()
        # issue_id 90 already got released by test_subscriber_stats
        assert parsed == "Undelivered Issues from: ['Kronen Zeitung: Issues with ID 1 ']"


def test_check_missingissues_with_unknown_subscriber(client, agency):
    response = client.get("/subscriber/50/missingissues")

    # test status code
    assert response.status_code == 404  # not found
