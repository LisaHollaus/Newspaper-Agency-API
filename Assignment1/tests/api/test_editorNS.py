# import the fixtures (this is necessary!)
from ..fixtures import app, client, agency


def test_get_editor_should_list_all_editors(client, agency):
    # send request
    response = client.get("/editor/")   # <-- note the slash at the end!

    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    assert len(parsed["editor"]) == len(agency.editors)


def test_post_add_editors(client, agency):
    # prepare
    editor_count_before = len(agency.editors)

    # act
    response = client.post("/editor/",  # <-- note the slash at the end!
                           json={
                               "ID": 1000,
                               "name": "Manuela",
                               "address": "Michelhausen 5"
                               })
    assert response.status_code == 200
    # verify

    assert len(agency.editors) == editor_count_before + 1
    # parse response and check that the correct data is here
    parsed = response.get_json()
    editor_response = parsed["editor"]

    # verify that the response contains the newspaper data
    assert editor_response["ID"] == 1000
    assert editor_response["name"] == "Manuela"
    assert editor_response["address"] == "Michelhausen 5"


def test_get_editor_should_list_specific_editor(client, agency):
    # send request
    response = client.get("/editor/1")   # using testdata

    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    paper_response = parsed["editor"]
    assert paper_response["ID"] == 1


def test_post_update_editor(client, agency):
    # act
    response = client.post("/editor/130",
                           json={
                               "ID": 130,
                               "name": "Josef",
                               "address": "Greenstreet 3"
                           })

    assert response.status_code == 200
    # parse response and check that the correct data is here
    parsed = response.get_json()
    paper_response = parsed["editor"]

    # verify that the response contains the newspaper data
    assert paper_response["ID"] == 130
    assert paper_response["name"] == "Josef"
    assert paper_response["address"] == "Greenstreet 3"


def test_post_update_editor_with_invalid_ID(client, agency):
    # act
    response = client.post("/editor/13",
                           json={
                               "ID": 13,
                               "name": "Joe",
                               "address": "Yellowstreet 3"
                           })

    assert response.status_code == 404  # not found


def test_delete_editor(client, agency):
    # prepare
    old_editor_list = len(agency.editors)
    # send request
    response = client.delete("/editor/108")

    # test status code
    assert response.status_code == 200

    # test if editor got deleted from the list
    new_editor_list = len(agency.editors)
    assert new_editor_list == old_editor_list - 1


def test_get_editor_issues(client, agency):
    # send request
    response = client.get("/editor/1/issues")  # using testdata

    # test status code
    assert response.status_code == 200

    # parse response and check that the correct data is here
    parsed = response.get_json()
    assert len(parsed["editor"]) == len(agency.editors[0].issues_list)


def test_get_editor_issues_unknown_editor(client, agency):
    # send request
    response = client.get("/editor/10000/issues")  # using testdata

    # test status code
    assert response.status_code == 404   # not found
