from typing import List, Union, Optional
from flask import jsonify

from .newspaper import Newspaper
from .editor import Editor
from .subscriber import Subscriber


class Agency(object):
    singleton_instance = None

    def __init__(self):
        self.newspapers: List[Newspaper] = []
        self.editors: List[Editor] = []
        self.subscribers: List[Subscriber] = []

    @staticmethod
    def get_instance():
        if Agency.singleton_instance is None:
            Agency.singleton_instance = Agency()
        return Agency.singleton_instance

    def add_newspaper(self, new_paper: Newspaper):
        for paper in self.newspapers:
            if paper == new_paper:
                # I used raise ValueError() instead of abort() in agency.py for better testing purposes
                raise ValueError(f"Newspaper named {new_paper.name} already exists")
            elif paper.paper_id == new_paper.paper_id:  # this shouldn't be possible if data was added only over the swagger interface
                raise ValueError(f'A newspaper with ID {new_paper.paper_id} already exists')
        self.newspapers.append(new_paper)
        return new_paper

    def get_newspaper(self, paper_id: int) -> Optional[Newspaper]:
        for paper in self.newspapers:
            if paper.paper_id == paper_id:
                return paper

    def all_newspapers(self) -> List[Newspaper]:
        return self.newspapers

    def remove_newspaper(self, paper: Newspaper):
        self.newspapers.remove(paper)

    def update_newspaper(self, targeted_paper, updated_paper):
        if targeted_paper == updated_paper:
            raise ValueError("Newspaper already up to date")
        # insuring that the paper keeps its subscriptions and issues
        updated_paper.issues = targeted_paper.issues
        updated_paper.subscribers = targeted_paper.subscribers
        self.newspapers[self.newspapers.index(targeted_paper)] = updated_paper
        return updated_paper

# issues:
    def add_issue(self, targeted_paper, new_issue):
        for issue in targeted_paper.issues:
            if issue == new_issue:
                raise ValueError("Issue already exists")
            elif issue.issue_id == new_issue.issue_id:
                raise ValueError(f'A issue with ID {issue.issue_id} already exists')
        # check if editor exists or still has to get assigned:
        if new_issue.editor_id != 0:
            editor = Agency.get_instance().get_editor(new_issue.editor_id)
            if not editor:
                raise ValueError(f"Editor with ID {new_issue.editor_id} was not found")
            editor.issues_list.append(new_issue)  # if editor exists
        targeted_paper.issues.append(new_issue)
        return new_issue

    def get_issue(self, paper, issue_id):
        for issue in paper.issues:
            if issue.issue_id == issue_id:
                return issue

    def all_issues(self, paper):
        return paper.issues

    def update_issue(self, targeted_paper, issue, updated_issue):
        if issue == updated_issue:
            raise ValueError("Issue already up to date")

        if updated_issue.editor_id != 0:
            editor = Agency.get_instance().get_editor(updated_issue.editor_id)
            if not editor:
                raise ValueError(f"Editor with ID {updated_issue.editor_id} was not found")
            if issue.editor_id == updated_issue.editor_id:  # no change
                editor.issues_list[editor.issues_list.index(issue)] = updated_issue  # replacing the old issue with updated version
            else:
                editor.issues_list.append(updated_issue)  # add issue to new editor
                if issue.editor_id != 0:  # check if there used to be another editor before
                    old_editor = Agency.get_instance().get_editor(issue.editor_id)
                    old_editor.issues_list.remove(issue)  # remove old issue from old editor

        targeted_paper.issues[targeted_paper.issues.index(issue)] = updated_issue  # replacing the old issue with updated version
        return updated_issue

    def remove_issue(self, targeted_paper, issue):
        targeted_paper.issues.remove(issue)
        if issue.editor_id != 0:
            editor = Agency.get_instance().get_editor(issue.editor_id)
            editor.issues_list.remove(issue)
        return jsonify(f"Issue with ID {issue.issue_id} was removed")

    def release_issue(self, issue):
        if issue.released:
            raise ValueError("Issue already released")
        elif issue.editor_id == 0:
            raise ValueError("Editor not yet specified!")
        issue.released = True
        return issue

    def add_editor_to_issue(self, issue, editor):
        if issue.editor_id == 0:
            issue.editor_id = editor.ID
            editor.issues_list.append(issue)
            return issue
        raise ValueError(f"Editor with ID {issue.editor_id} is already the editor of this Issue")

    def deliver_issue(self, subscriber, issue, targeted_paper):
        if not issue.released:
            raise ValueError(f"Issue {issue.issue_id} hasn't been released yet")
        # the subscriber can subscribe/receive special issues, therefore the next two lines are not necessary
        # elif targeted_paper not in subscriber.newspaper_list:
            # raise ValueError(f"The Subscriber has no subscription for the newspaper {targeted_paper.name}")
        elif issue in subscriber.issues_list:
            raise ValueError(f"Issue {issue.issue_id} has already been delivered")
        subscriber.issues_list.append(issue)
        return jsonify(f"Issue {issue.issue_id} from {targeted_paper.name} delivered")

    def newspaper_stats(self, paper):
        subscriber_number = len(paper.subscribers)
        return jsonify(f"{paper.name} stats: "
                       f"Number of Subscribers: {subscriber_number} "
                       f"Monthly revenue: {subscriber_number * paper.price} "
                       f"Annual revenue: {subscriber_number * paper.price * 12}")

# editor:
    def add_editor(self, new_editor: Editor):
        for editor in self.editors:
            if new_editor == editor:
                raise ValueError(f"Editor {new_editor.name} already exists")
            elif new_editor.ID == editor.ID:
                raise ValueError(f"A editor with ID {new_editor.ID} already exists")
        self.editors.append(new_editor)
        return new_editor

    def all_editors(self):
        return self.editors

    def get_editor(self, editor_id: Union[int,str]) -> Optional[Editor]:
        for editor in self.editors:
            if editor.ID == editor_id:
                return editor

    def update_editor(self, targeted_editor, updated_editor):
        if targeted_editor == updated_editor:
            raise ValueError("No changes made")
        # insuring the editor keeps its issues and newspaper lists:
        updated_editor.issues_list = targeted_editor.issues_list
        updated_editor.newspaper_list = targeted_editor.newspaper_list
        self.editors[self.editors.index(targeted_editor)] = updated_editor
        return updated_editor

    def remove_editor(self, editor: Editor):
        self.editors.remove(editor)
        if len(editor.issues_list) != 0 and len(self.editors) != 0:  # if the editor had issues in his/her supervision  # and there are other editors
            for issue in editor.issues_list:
                for new_editor in self.editors:
                    newspaper_list = [x.newspaper_id for x in new_editor.issues_list]  # id_list of all newspapers an editor works for
                    if issue.newspaper_id in newspaper_list:
                        new_editor.issues_list.append(issue)  # transferring issues of the deleted editor to another editor
                        break


    def get_editor_issues(self, editor: Editor):
        return editor.issues_list

# subscriber:
    def add_subscriber(self, new_subscriber: Subscriber):
        for subscriber in self.subscribers:
            if new_subscriber.ID == subscriber.ID:
                raise ValueError(f"A subscriber with ID {new_subscriber.ID} already exists")
            elif new_subscriber == subscriber:
                raise ValueError(f"Subscriber {new_subscriber.name} already exists")
        self.subscribers.append(new_subscriber)
        return new_subscriber

    def all_subscribers(self) -> List[Subscriber]:
        return self.subscribers

    def get_subscriber(self, subscriber_id: Union[int,str]) -> Optional[Subscriber]:
        for subscriber in self.subscribers:
            if subscriber.ID == subscriber_id:
                return subscriber

    def update_subscriber(self, targeted_subscriber, updated_subscriber):
        if targeted_subscriber == updated_subscriber:
            raise ValueError(f"No changes made")
        # insuring the subscriber keeps its issues and newspaper lists:
        updated_subscriber.issues_list = targeted_subscriber.issues_list
        updated_subscriber.newspaper_list = targeted_subscriber.newspaper_list
        self.subscribers[self.subscribers.index(targeted_subscriber)] = updated_subscriber
        return updated_subscriber

    def remove_subscriber(self, subscriber: Subscriber):
        for paper in self.newspapers:
            if subscriber in paper.subscribers:
                paper.subscribers.remove(subscriber)  # stops all subscriptions when subscriber is deleted
        self.subscribers.remove(subscriber)

    def subscribe_to_paper(self, subscriber, paper):
        if subscriber not in paper.subscribers:
            paper.subscribers.append(subscriber)
            # then paper also not in subscriber.newspaper_list:
            subscriber.newspaper_list.append(paper)
            return jsonify("Done!")
        raise ValueError(f"Subscriber {subscriber.ID} already has a subscription of the Newspaper {paper.name}")

    def get_subscriber_stats(self, subscriber):
        newspaper_number = len(subscriber.newspaper_list)
        monthly_cost = 0
        newspaper_issues = {}
        # subscriptions:
        if newspaper_number != 0:
            monthly_cost = sum([x.price for x in subscriber.newspaper_list])
            for paper in subscriber.newspaper_list:
                for issue in paper.issues:
                    if issue in subscriber.issues_list:
                        newspaper_issues.update({paper.name: 1 + newspaper_issues.get(paper.name,0)})

        # special issues are not in the newspaper_list:
        special_issues = ""
        if subscriber.issues_list != 0:
            newspaper_IDs = [paper.paper_id for paper in subscriber.newspaper_list]
            for issue in subscriber.issues_list:
                if issue.newspaper_id not in newspaper_IDs:
                    paper = Agency.get_instance().get_newspaper(issue.newspaper_id)
                    special_issues += f"Issue with ID {issue.issue_id} from '{paper.name}', "

        return jsonify(f"Number of newspaper subscriptions: {newspaper_number} "
                       f"Cost: {monthly_cost} monthly or {monthly_cost * 12} annually "  # special issues not included (Assuming special issues are paid directly) 
                       f"Number of Issues received from: {str([key+': '+str(value) for key, value in newspaper_issues.items()])} "
                       f"Special issues without subscription: {special_issues}")

    def check_missingissues(self, subscriber):
        undelivered = {}
        for paper in subscriber.newspaper_list:
            for issue in paper.issues:
                if issue.released and (issue not in subscriber.issues_list):  # and ({paper.name: str(issue)} not in undelivered):
                    undelivered.update({paper.name: str(issue.issue_id) + undelivered.get(' '+paper.name, "")})
        return f"Undelivered Issues from: {[key+': Issues with ID '+str(value)+' ' for key, value in undelivered.items()]}"
