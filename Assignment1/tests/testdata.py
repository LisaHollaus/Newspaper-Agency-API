from ..src.model.agency import Agency
from ..src.model.newspaper import Newspaper
from ..src.model.editor import Editor
from ..src.model.subscriber import Subscriber
from ..src.model.issue import Issue


def create_newspapers(agency: Agency):
    paper1 = Newspaper(paper_id=100, name="The New York Times", frequency=7, price=13.14)  # all testdata issues are publicated to this newspaper # updated by test_update_newspaper
    paper2 = Newspaper(paper_id=101, name="Heute", frequency=1, price=1.12)  # updated by test_update_newspaper
    paper3 = Newspaper(paper_id=115, name="Wall Street Journal", frequency=1, price=3.00)  # issue 1 & 2 added by test_post_add_issues and test_check_missingissues
    paper4 = Newspaper(paper_id=125, name="National Geographic", frequency=30, price=34.00)  # deleted by test_delete_newspaper
    paper5 = Newspaper(paper_id=135, name="Kronen Zeitung", frequency=15, price=30.00)  # issue_id 1, 10 & 20 added by test_get_check_missingissues, test_add_issue & test_update_issue
    agency.newspapers.extend([paper1, paper2, paper3, paper4, paper5])


def create_issues(newspaper: Newspaper):
    issue1 = Issue(issue_id=90, releasedate=2024-10-15, released=False, editor_id=1, pages=33, newspaper_id=newspaper.paper_id)  # released and delivered to subscriber 10 by test_subscriber_stats
    issue2 = Issue(issue_id=91, releasedate=2024-10-17, released=False, editor_id=0, pages=23, newspaper_id=newspaper.paper_id)  # not released for test_deliver_issue_not_released
    issue3 = Issue(issue_id=92, releasedate=2024-11-19, released=False, editor_id=102, pages=23, newspaper_id=newspaper.paper_id)  # delivered to subscriber 180 by test_deliver_issue
    issue4 = Issue(issue_id=93, releasedate=2024-11-25, released=False, editor_id=1, pages=10, newspaper_id=newspaper.paper_id)  # test_get_specific_issue  # test_post_update_issue
    issue5 = Issue(issue_id=94, releasedate=2023-12-16, released=False, editor_id=1, pages=5, newspaper_id=newspaper.paper_id)  # test_release_issue
    issue6 = Issue(issue_id=95, releasedate=2024-12-18, released=False, editor_id=0, pages=5, newspaper_id=newspaper.paper_id)  # editor 1 added by test_post_editor_to_issue # delivered to subscriber 103 by test_post_deliver_issue
    issue7 = Issue(issue_id=96, releasedate=2024-12-28, released=False, editor_id=1, pages=30, newspaper_id=newspaper.paper_id)  # issue released by test_post_release_issue
    issue8 = Issue(issue_id=97, releasedate=2024-10-28, released=False, editor_id=0, pages=30, newspaper_id=newspaper.paper_id)  # editor 1 added by test_add_editor_to_issue
    newspaper.issues.extend([issue1, issue2, issue3, issue4, issue5, issue6, issue7, issue8])


def create_editor(agency: Agency):  # for simplicity, I just added first names
    editor1 = Editor(ID=1, name="Gustav", address="Vikingstreet 3")
    editor2 = Editor(ID=102, name="Katherina", address="Osterhasen 27")
    editor3 = Editor(ID=108, name="Osiris", address="Pyramidsstreet 42")  # deleted by test_delete_editor
    editor4 = Editor(ID=130, name="Josef", address="Josefstreet 9")  # updated by test_post_update_editor
    editor5 = Editor(ID=131, name="Joey", address="Joeystreet 9")  # updated by test_update_editor
    agency.editors.extend([editor1, editor2, editor3, editor4, editor5])


def create_subscribers(agency: Agency):  # for simplicity, I just added first names
    subscriber1 = Subscriber(ID=10, name="Anton", address="Kufsteinstraße 99")  # subscribed to paper_id 100 and issue_id 90 delivered by test_get_subscriber_stats  # updated by test_update_subscriber
    subscriber2 = Subscriber(ID=103, name="Medusa", address="Gorgonstreet 150")  # subscribed to paper_id 100 and issue_id 95 delivered by test_deliver_issue  # subscribed to paper_id 115 and removed by test_subscribe_to_paper
    subscriber3 = Subscriber(ID=120, name="Emil", address="Elaphantstreet 8")  # deleted by test_delete_subscriber
    subscriber4 = Subscriber(ID=150, name="Emilia", address="Mamuthallee 35")  # updated by test_post_update_subscriber  # subscribed to paper_id 115 by test_check_missingissues
    subscriber5 = Subscriber(ID=160, name="Emanuel", address="Treestreet 36")  # subscribed to paper_id 100 by test_post_subscribe_to_a_newspaper
    subscriber6 = Subscriber(ID=170, name="Alisa", address="Flowerstreet 37")  # subscribed to paper_id 135 by test_get_check_missingissues  # not subscribed to paper_id 100 for test_deliver_issue_without_subscription
    subscriber7 = Subscriber(ID=180, name="Alfred", address="Flowerstreet 37")  # subscribed to paper_id 100 and delivered isssue_id 92 by test_deliver_issue
    agency.subscribers.extend([subscriber1, subscriber2, subscriber3, subscriber4, subscriber5, subscriber6, subscriber7])


def populate(agency: Agency):
    create_newspapers(agency)
    create_editor(agency)
    create_subscribers(agency)


def populate_issues(newspaper: Newspaper):
    create_issues(newspaper)

