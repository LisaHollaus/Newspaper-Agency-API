# import the fixtures (this is necessary!)
from ..fixtures import app, client, agency


def test_get_newspaper_should_list_all_papers(client, agency):
    # send request
    response = client.get("/newspaper/")   # <-- note the slash at the end!

    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    assert len(parsed["newspapers"]) == len(agency.newspapers)


def test_add_newspaper(client, agency):
    # prepare
    paper_count_before = len(agency.newspapers)

    # act
    response = client.post("/newspaper/",  # <-- note the slash at the end!
                           json={
                               "paper_id": 10,
                               "name": "Simpsons Comic",
                               "frequency": 8,
                               "price": 3.15
                           })
    assert response.status_code == 200
    # verify
    assert len(agency.newspapers) == paper_count_before + 1
    # parse response and check that the correct data is here
    parsed = response.get_json()
    paper_response = parsed["newspaper"]

    # verify that the response contains the newspaper data
    assert paper_response["paper_id"] == 10
    assert paper_response["name"] == "Simpsons Comic"
    assert paper_response["frequency"] == 8
    assert paper_response["price"] == 3.15


def test_get_newspaper_should_list_specific_papers(client, agency):
    # send request
    response = client.get("/newspaper/100")   # using testdata

    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    paper_response = parsed["newspaper"]
    assert paper_response["paper_id"] == 100


def test_update_newspaper(client, agency):
    # act
    response = client.post("/newspaper/101",  # using testdata
                           json={
                               "paper_id": 101,
                               "name": "Heute",
                               "frequency": 10,
                               "price": 5.00
                           })

    assert response.status_code == 200
    # parse response and check that the correct data is here
    parsed = response.get_json()
    paper_response = parsed["newspaper"]

    # verify that the response contains the newspaper data
    assert paper_response["paper_id"] == 101
    assert paper_response["name"] == "Heute"
    assert paper_response["frequency"] == 10
    assert paper_response["price"] == 5.00


def test_update_newspaper_with_invalid_ID(client, agency):
    # act
    response = client.post("/newspaper/100001",
                           json={
                               "paper_id": 100001,
                               "name": "Heute",
                               "frequency": 10,
                               "price": 5.00
                           })

    assert response.status_code == 404  # not found


def test_delete_newspaper(client, agency):
    # arrange
    old_newspaper_list = len(agency.newspapers)
    # send request
    response = client.delete("/newspaper/125")

    # test status code
    assert response.status_code == 200

    # test if newspaper got deleted from the list
    new_newspaper_list = len(agency.newspapers)
    assert new_newspaper_list == old_newspaper_list - 1


# issues:
def test_get_issues_should_list_all_issues(client, agency):
    # arrange
    paper = agency.get_newspaper(100)  # using testdata

    # send request
    response = client.get("/newspaper/100/issue")

    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    assert len(parsed["issues"]) == len(paper.issues)


def test_get_issues_without_newspaper(client, agency):
    # act
    response = client.get("/newspaper/343451/issue")  # using testdata

    # test status code
    assert response.status_code == 404  # not found


def test_post_add_issues(client, agency):
    # arrange
    paper = agency.get_newspaper(115)
    issue_count_before = len(paper.issues)
    # act
    response = client.post("/newspaper/115/issue",
                           json={
                               "issue_id": 1,
                               "releasedate": "2025-12-17",
                               "released": False,
                               "editor_id": 0,
                               "pages": 70
                           })
    assert response.status_code == 200
    # verify
    assert len(paper.issues) == issue_count_before + 1
    # parse response and check that the correct data is here
    parsed = response.get_json()
    paper_response = parsed["issue"]

    # verify that the response contains the issue data
    assert paper_response["issue_id"] == 1
    assert paper_response["releasedate"] == "2025-12-17"
    assert paper_response["released"] == False
    assert paper_response["editor_id"] == 0
    assert paper_response["pages"] == 70


def test_post_add_issues_with_unknown_paper(client, agency):
    # act
    response = client.post("/newspaper/1010101/issue",
                           json={
                               "issue_id": 1,
                               "releasedate": "2025-12-17",
                               "released": False,
                               "editor_id": 0,
                               "pages": 70
                           })
    # test status code
    assert response.status_code == 404  # not found


def test_get_specific_issue(client, agency):
    # send request
    response = client.get("/newspaper/100/issue/93")   # using testdata

    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    paper_response = parsed["issue"]
    assert paper_response["issue_id"] == 93


def test_get_specific_issue_with_unknown_paper(client, agency):
    # send request
    response = client.get("/newspaper/1099/issue/93")   # using testdata

    # test status code
    assert response.status_code == 404  # not found


def test_get_specific_issue_unknown_issue(client, agency):
    # send request
    response = client.get("/newspaper/100/issue/933")   # using testdata

    # test status code
    assert response.status_code == 404  # not found


def test_post_update_issue(client, agency):
    # act
    response = client.post("/newspaper/100/issue/93",  # using testdata
                           json={
                               "issue_id": 9873,  # should stay the original id
                               "releasedate": "2025-10-15",
                               "released": True,  # should not be possible to change
                               "editor_id": 0,
                               "pages": 15
                           })
    # test status code
    assert response.status_code == 200
    # parse response and check that the correct data is here
    parsed = response.get_json()
    paper_response = parsed["issue"]

    # verify that the response contains the issue data
    assert paper_response["issue_id"] == 93
    assert paper_response["releasedate"] == "2025-10-15"
    assert paper_response["released"] == False
    assert paper_response["editor_id"] == 0
    assert paper_response["pages"] == 15


def test_post_update_issue_with_unknown_paper(client, agency):
    # act
    response = client.post("/newspaper/12300/issue/93",  # using testdata
                           json={
                               "issue_id": 9873,  # should stay the original id
                               "releasedate": "2025-10-15",
                               "released": True,  # should not be possible to change
                               "editor_id": 0,
                               "pages": 15
                           })
    # test status code
    assert response.status_code == 404  # not found


def test_post_update_issue_with_unknown_issue(client, agency):
    # act
    response = client.post("/newspaper/100/issue/91233",  # using testdata
                           json={
                               "issue_id": 9873,  # should stay the original id
                               "releasedate": "2025-10-15",
                               "released": True,  # should not be possible to change
                               "editor_id": 0,
                               "pages": 15
                           })
    # test status code
    assert response.status_code == 404  # not found


def test_delete_issue(client, agency):
    # arrange
    paper = agency.get_newspaper(100)  # using testdata
    old_issue_list = len(paper.issues)
    # adding new issue first
    response = client.post("/newspaper/100/issue",
                           json={
                               "issue_id": 2,
                               "releasedate": "2025-11-17",
                               "released": False,
                               "editor_id": 1,
                               "pages": 77
                           })
    assert response.status_code == 200
    assert old_issue_list + 1 == len(paper.issues)

    # act
    response = client.delete("/newspaper/100/issue/2")

    # test status code
    assert response.status_code == 200

    # test if issue got deleted from the newspapers list
    assert old_issue_list == len(paper.issues)


def test_delete_issue_with_unknown_paper(client, agency):
    # send request
    response = client.delete("/newspaper/1234321/issue/5")

    # test status code
    assert response.status_code == 404  # not found


def test_delete_issue_with_unknown_issue(client, agency):
    # arrange
    paper = agency.get_newspaper(101)
    old_issue_list = len(paper.issues)

    # send request
    response = client.delete("/newspaper/101/issue/5")

    # test status code
    assert response.status_code == 404  # not found

    # asserting that nothing got deleted
    assert old_issue_list == len(paper.issues)


def test_post_release_issue(client, agency):
    # arrange
    newspaper = agency.get_newspaper(100)
    issue = agency.get_issue(newspaper, 96)
    assert issue.released is False

    # act
    response = client.post("/newspaper/100/issue/96/release")

    # test status code
    assert response.status_code == 200

    # test if issue got released
    parsed = response.get_json()
    issue_response = parsed["issue"]
    assert issue_response["released"]
    assert issue.released


def test_post_release_issue_with_unknown_paper(client, agency):
    # send request
    response = client.post("/newspaper/1009/issue/96/release")

    # test status code
    assert response.status_code == 404  # not found


def test_post_release_issue_with_unknown_issue(client, agency):
    # send request
    response = client.post("/newspaper/100/issue/196/release")

    # test status code
    assert response.status_code == 404  # not found


def test_post_editor_to_issue(client, agency):
    # arrange
    newspaper = agency.get_newspaper(100)
    issue = agency.get_issue(newspaper, 95)
    assert issue.editor_id == 0

    # act
    response = client.post("/newspaper/100/issue/95/editor",
                           json={
                               "ID": 1
                           })

    # test status code
    assert response.status_code == 200

    # test editor got set
    parsed = response.get_json()
    issue_response = parsed["issue"]
    assert issue_response["editor_id"]
    assert issue.editor_id == 1


def test_post_editor_to_issue_with_unknown_editor(client, agency):
    # arrange
    newspaper = agency.get_newspaper(100)
    issue = agency.get_issue(newspaper, 91)
    assert issue.editor_id == 0

    # act
    response = client.post("/newspaper/100/issue/95/editor",
                           json={
                               "ID": 15  # editor ID
                           })

    # test status code
    assert response.status_code == 404  # not found
    assert issue.editor_id == 0  # no changes made


def test_post_editor_to_issue_with_unknown_paper(client, agency):
    # act
    response = client.post("/newspaper/1000000/issue/95/editor",
                           json={
                               "ID": 1  # editor ID
                           })
    # test status code
    assert response.status_code == 404  # not found


def test_post_editor_to_issue_with_unknown_issue(client, agency):
    # act
    response = client.post("/newspaper/100/issue/955/editor",
                           json={
                               "ID": 1  # editor ID
                           })
    # test status code
    assert response.status_code == 404  # not found


def test_post_deliver_issue(client, agency, app):
    with app.app_context():
        # arrange
        newspaper = agency.get_newspaper(100)
        issue = agency.get_issue(newspaper, 95)
        subscriber = agency.get_subscriber(103)
        agency.subscribe_to_paper(subscriber, newspaper)
        agency.release_issue(issue)
        before = len(subscriber.issues_list)

        # send request
        response = client.post("/newspaper/100/issue/95/deliver",
                               json={
                                   "ID": 103  # subscriber ID
                               })
        # test status code
        assert response.status_code == 200

        # assert that issue got added
        assert before + 1 == len(subscriber.issues_list)


def test_post_deliver_issue_with_unknown_subscriber(client, agency):
    # act
    response = client.post("/newspaper/100/issue/95/deliver",
                           json={
                                   "ID": 10333  # subscriber id
                                })
    # test status code
    assert response.status_code == 404  # not found


def test_post_deliver_issue_with_unknown_paper(client, agency):
    # act
    response = client.post("/newspaper/1000000/issue/95/deliver",
                           json={
                                   "ID": 150  # subscriber id
                                })
    # test status code
    assert response.status_code == 404  # not found


def test_post_deliver_issue_with_unknown_issue(client, agency):
    # act
    response = client.post("/newspaper/100/issue/795/deliver",
                           json={
                                   "ID": 150  # subscriber id
                                })
    # test status code
    assert response.status_code == 404  # not found


def test_get_info_about_a_specific_paper(client, agency):
    # send request
    response = client.get("/newspaper/100/stats")

    # test status code
    assert response.status_code == 200

    parsed = response.get_json()
    assert parsed == (f"The New York Times stats: "
                      f"Number of Subscribers: 1 "
                      f"Monthly revenue: 13.14 "
                      f"Annual revenue: 157.68")


def test_get_info_about_a_specific_paper_with_unknown_paper(client, agency):
    # send request
    response = client.get("/newspaper/10098/stats")

    # test status code
    assert response.status_code == 404  # not found
