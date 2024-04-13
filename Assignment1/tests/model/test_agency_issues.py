import pytest

from ...src.model.issue import Issue
from ..fixtures import app, client, agency


# adding and getting all issues:
def test_add_issue(agency, app):
    with app.app_context():
        paper = agency.get_newspaper(135)  # using testdata
        before = len(paper.issues)
        new_issue = Issue(issue_id=10,
                          releasedate=2025-12-13,
                          released=False,  # Initially, paper issues are not published
                          editor_id=1,  # exists in testdata
                          pages=12)
        agency.add_issue(paper, new_issue)
        assert len(agency.all_issues(paper)) == before + 1


def test_add_issue_same_id_should_raise_error(agency, app):
    with app.app_context():
        paper = agency.get_newspaper(100)  # using testdata
        before = len(paper.issues)
        new_issue = Issue(issue_id=1111,
                          releasedate=2025-12-16,
                          released=False,  # Initially, paper issues are not published
                          editor_id=1,  # exists in testdata
                          pages=5)
        # first adding of newspaper should be okay
        agency.add_issue(paper, new_issue)
        new_issue2 = Issue(issue_id=1111,
                           releasedate=2025-12-25,
                           released=False,  # Initially, paper issues are not published
                           editor_id=1,  # exists in testdata
                           pages=32)
        with pytest.raises(ValueError, match='A issue with ID 1111 already exists'):  # <-- this allows us to test for exceptions
            # this one should raise an exception!
            agency.add_issue(paper, new_issue2)
        assert len(agency.all_issues(paper)) == before + 1  # make sure only 1 newspaper got added to the list


def test_add_issue_same_issue_should_raise_error(agency, app):
    with app.app_context():
        paper = agency.get_newspaper(101)  # using testdata
        before = len(paper.issues)
        new_issue = Issue(issue_id=2222,
                          releasedate=2025-12-16,
                          released=False,  # Initially, paper issues are not published
                          editor_id=1,  # exists in testdata
                          pages=17,
                          newspaper_id=paper.paper_id)
        # first adding of newspaper should be okay
        agency.add_issue(paper, new_issue)
        new_issue2 = Issue(issue_id=3333,
                           releasedate=2025-12-16,
                           released=False,  # Initially, paper issues are not published
                           editor_id=1,  # exists in testdata
                           pages=17,
                           newspaper_id=paper.paper_id)
        with pytest.raises(ValueError, match='Issue already exists'):  # <-- this allows us to test for exceptions
            # this one should raise an exception!
            agency.add_issue(paper, new_issue2)
        assert len(agency.all_issues(paper)) == before + 1  # make sure only 1 newspaper got added to the list


def test_add_issue_with_unknown_editor_should_raise_error(agency, app):
    with app.app_context():
        paper = agency.get_newspaper(115)  # using testdata
        before = len(paper.issues)
        new_issue = Issue(issue_id=2000,
                          releasedate=2025-10-21,
                          released=False,  # Initially, paper issues are not published
                          editor_id=2,  # does not exist in testdata
                          pages=12,
                          newspaper_id=paper.paper_id)
        with pytest.raises(ValueError, match='Editor with ID 2 was not found'):
            # this one should raise an exception!
            agency.add_issue(paper, new_issue)
        assert len(agency.all_issues(paper)) == before


# getting an issue by ID:
def test_get_issue_by_id(agency, app):
    with app.app_context():
        paper = agency.get_newspaper(101)  # using testdata
        issue_id = 12
        releasedate = 2025-12-10
        released = False  # Initially, paper issues are not published
        editor_id = 1  # exists in testdata
        pages = 20
        new_issue = Issue(issue_id=issue_id,
                          releasedate=releasedate,
                          released=released,  # Initially, paper issues are not published
                          editor_id=editor_id,  # exists in testdata
                          pages=pages,
                          newspaper_id=paper.paper_id)
        agency.add_issue(paper, new_issue)
        get_issue = agency.get_issue(paper, issue_id)
        assert get_issue.issue_id == issue_id
        assert get_issue.releasedate == releasedate
        assert get_issue.released == released
        assert get_issue.editor_id == editor_id
        assert get_issue.pages == pages
        assert get_issue.newspaper_id == paper.paper_id


# updating an issue:
def test_update_issue(agency, app):
    with app.app_context():
        # arrange
        paper = agency.get_newspaper(135)  # using testdata
        old_issue = Issue(issue_id=20,
                          releasedate=2025-11-21,
                          released=False,
                          editor_id=1,
                          pages=12,
                          newspaper_id=paper.paper_id)
        agency.add_issue(paper, old_issue)

        updated_issue = Issue(issue_id=20,
                              releasedate=2025-10-12,
                              released=False,
                              editor_id=102,
                              pages=10,
                              newspaper_id=paper.paper_id)
        # act
        agency.update_issue(paper, old_issue, updated_issue)
        print(old_issue, updated_issue)
        get_issue = agency.get_issue(paper, 20)
        assert old_issue != updated_issue
        assert updated_issue == get_issue
        assert get_issue.issue_id == 20


# remove an issue:
def test_remove_issue(agency, app):
    with app.app_context():
        # arrange
        paper = agency.get_newspaper(101)  # using testdata
        before = len(paper.issues)
        new_issue = Issue(issue_id=2001,
                          releasedate=2025-10-14,
                          released=False,  # Initially, paper issues are not published
                          editor_id=1,
                          pages=12,
                          newspaper_id=paper.paper_id)
        agency.add_issue(paper, new_issue)
        assert len(agency.all_issues(paper)) == before + 1
        # act
        agency.remove_issue(paper, new_issue)
        assert len(agency.all_issues(paper)) == before


# release an issue:
def test_release_issue(agency, app):
    with app.app_context():
        paper = agency.get_newspaper(100)  # using testdata
        issue = agency.get_issue(paper, 94)  # using testdata
        assert issue.released is False
        agency.release_issue(issue)
        assert issue.released is True
        with pytest.raises(ValueError, match='Issue already released'):
            # releasing an issue twice should raise an exception!
            agency.release_issue(issue)
        assert issue.released is True  # making sure there's no change


def test_release_issue_without_editor(agency, app):
    with app.app_context():
        paper = agency.get_newspaper(100)  # using testdata
        issue = agency.get_issue(paper, 97)  # using testdata without an editor
        assert issue.released is False
        assert issue.editor_id == 0
        with pytest.raises(ValueError, match='Editor not yet specified!'):
            # this one should raise an exception!
            agency.release_issue(issue)
        assert issue.released is False  # making sure there's no change


# add editor to issue:
def test_add_editor_to_issue(agency, app):
    with app.app_context():
        paper = agency.get_newspaper(100)  # using testdata
        editor = agency.get_editor(1)  # using testdata
        issue = agency.get_issue(paper, 97)  # using testdata without an editor
        assert issue.editor_id == 0
        agency.add_editor_to_issue(issue, editor)
        assert issue.editor_id == editor.ID
        with pytest.raises(ValueError, match=f"Editor with ID {issue.editor_id} is already the editor of this Issue"):
            # specifying an editor twice should raise an exception!
            agency.add_editor_to_issue(issue, editor)
        assert issue.editor_id == editor.ID  # making sure there's no change


# deliver issue:
def test_deliver_issue(agency, app):
    with app.app_context():
        # arrange
        paper = agency.get_newspaper(100)  # using testdata
        issue = agency.get_issue(paper, 92)  # using testdata
        subscriber = agency.get_subscriber(180)
        agency.subscribe_to_paper(subscriber, paper)
        agency.release_issue(issue)
        before = len(subscriber.issues_list)
        # act
        agency.deliver_issue(subscriber, issue, paper)
        assert len(subscriber.issues_list) == before + 1
        with pytest.raises(ValueError, match=f"Issue {issue.issue_id} has already been delivered"):
            # to make sure an issue is delivered only once
            agency.deliver_issue(subscriber, issue, paper)
        assert len(subscriber.issues_list) == before + 1


def test_deliver_issue_not_released(agency, app):
    with app.app_context():
        paper = agency.get_newspaper(100)  # using testdata
        issue = agency.get_issue(paper, 91)  # using testdata
        subscriber = agency.get_subscriber(180)
        # agency.subscribe_to_paper(subscriber,paper)  # paper already subscribed by test_deliver_issue
        # agency.release_issue(issue) # not releasing the issue
        before = len(subscriber.issues_list)
        with pytest.raises(ValueError, match=f"Issue {issue.issue_id} hasn't been released yet"):
            # this one should raise an exception!
            agency.deliver_issue(subscriber, issue, paper)
        assert len(subscriber.issues_list) == before
