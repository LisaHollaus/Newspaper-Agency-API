import pytest

from ...src.model.editor import Editor
from ..fixtures import app, client, agency


# adding and getting all editors:
def test_add_editor(agency):
    before = len(agency.editors)
    new_editor = Editor(ID=111,
                        name="Jimmy",
                        address="Treestreet 3")
    agency.add_editor(new_editor)
    assert len(agency.all_editors()) == before + 1


def test_add_editor_same_id_should_raise_error(agency):
    before = len(agency.editors)
    new_editor = Editor(ID=99,
                        name="Simone",
                        address="Treestreet 4")
    agency.add_editor(new_editor)
    new_editor2 = Editor(ID=99,
                         name="Simon",
                         address="Treestreet 3")
    with pytest.raises(ValueError, match='A editor with ID 99 already exists'):
        # this one should rais ean exception!
        agency.add_editor(new_editor2)
    assert len(agency.all_editors()) == before + 1  # making sure only 1 editor got added to the list


def test_add_editor_same_person_should_raise_error(agency):
    before = len(agency.editors)
    new_editor = Editor(ID=12,
                        name="Lily",
                        address="Treestreet 3")
    agency.add_editor(new_editor)
    new_editor2 = Editor(ID=12,
                         name="Lily",
                         address="Treestreet 3")
    with pytest.raises(ValueError, match='Editor Lily already exists'):
        # this one should rais ean exception!
        agency.add_editor(new_editor2)
    assert len(agency.all_editors()) == before + 1  # making sure only 1 editor got added to the list


# getting an editor by ID:
def test_get_editor_by_id(agency):
    ID = 12222
    name = "John"
    address = "221b Bakerstreet"
    new_editor = Editor(ID=ID,
                        name=name,
                        address=address)
    agency.add_editor(new_editor)
    get_editor = agency.get_editor(ID)
    assert get_editor.ID == ID
    assert get_editor.name == name
    assert get_editor.address == address


# remove a editor:
def test_remove_editor(agency):
    before = len(agency.editors)
    new_editor = Editor(ID=122,
                        name="Leo",
                        address="Avenuestreet 1")
    agency.add_editor(new_editor)
    assert len(agency.all_editors()) == before + 1
    agency.remove_editor(new_editor)
    assert len(agency.all_editors()) == before


# update Editor:
def test_update_editor(agency, app):
    with app.app_context():
        old_editor = agency.get_editor(131)  # using testdata
        ID = old_editor.ID
        name = "another name"
        address = "somewhere else"
        updated_editor = Editor(ID=ID,
                                name=name,
                                address=address)
        agency.update_editor(old_editor, updated_editor)
        get_editor = agency.get_editor(ID)
        assert old_editor != updated_editor and old_editor != get_editor
        assert updated_editor == get_editor
        assert get_editor.ID == ID
        # making sure the editor keeps its issues and newspapers:
        assert get_editor.issues_list == updated_editor.issues_list
        assert get_editor.newspaper_list == updated_editor.issues_list
        with pytest.raises(ValueError, match="No changes made"):
            # updating editor without a change should raise an exception!
            agency.update_editor(updated_editor, updated_editor)


# get editors issues list:
def test_get_editor_issues(agency, app):
    with app.app_context():
        paper = agency.get_newspaper(100)  # using testdata
        issue = agency.get_issue(paper, 91)  # using testdata
        editor = agency.get_editor(1)
        before = len(editor.issues_list)
        agency.add_editor_to_issue(issue, editor)
        assert len(editor.issues_list) == before + 1
        assert editor.issues_list == agency.get_editor_issues(editor)
