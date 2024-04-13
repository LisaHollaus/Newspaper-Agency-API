from flask import jsonify
from flask_restx import Namespace, reqparse, Resource, fields, abort

from ..model.agency import Agency
from ..model.newspaper import Newspaper
from ..model.issue import Issue

newspaper_ns = Namespace("newspaper", description="Newspaper related operations")

paper_model = newspaper_ns.model('NewspaperModel', {
    'paper_id': fields.Integer(required=False,
                               help='The unique identifier of a newspaper'),
    'name': fields.String(required=True,
                          help='The name of the newspaper, e.g. The New York Times'),
    'frequency': fields.Integer(required=True,
                                help='The publication frequency of the newspaper in days (e.g. 1 for daily papers and 7 for weekly magazines'),
    'price': fields.Float(required=True,
                          help='The monthly price of the newspaper (e.g. 12.3)')
   })

issue_model = newspaper_ns.model('Issue Model', {
    'issue_id': fields.Integer(required=False,
                               help='The unique identifier of a issue'),
    'releasedate': fields.String(required=True,  # .Date instead of String would seem more fitting, but it interfered with my testdata
                                 help='The release date of an Newspaper Issue'),
    'released': fields.Boolean(required=False,
                               help='True if the issue is released'),
    'editor_id': fields.Integer(required=True,
                                help='The editor of the Issue'),
    'pages': fields.Integer(required=True,
                            help='The number of pages')
   })

ID_model = newspaper_ns.model('IDModel', {
    'ID': fields.Integer(required=True,
                         help='The unique identifier')
})


@newspaper_ns.route('/')
class NewspaperAPI(Resource):

    @newspaper_ns.doc(paper_model, description="Add a new newspaper")
    @newspaper_ns.expect(paper_model, validate=True)
    @newspaper_ns.marshal_with(paper_model, envelope='newspaper')
    def post(self):
        # creating a unique ID (optional: customised if not jet existing)
        paper_id = newspaper_ns.payload['paper_id']
        IDs = [x.paper_id for x in Agency.get_instance().newspapers]
        while True:
            if paper_id not in IDs:
                break
            paper_id += 1
        # create a new paper object and add it
        new_paper = Newspaper(paper_id=paper_id,
                              name=newspaper_ns.payload['name'],
                              frequency=newspaper_ns.payload['frequency'],
                              price=newspaper_ns.payload['price'])
        return Agency.get_instance().add_newspaper(new_paper)

    @newspaper_ns.doc(description="Get all newspapers")
    @newspaper_ns.marshal_list_with(paper_model, envelope='newspapers')
    def get(self):
        return Agency.get_instance().all_newspapers()


@newspaper_ns.route('/<int:paper_id>')
class NewspaperID(Resource):
    @newspaper_ns.doc(description="Get a new newspaper")
    @newspaper_ns.marshal_with(paper_model, envelope='newspaper')
    def get(self, paper_id):
        search_result = Agency.get_instance().get_newspaper(paper_id)
        return search_result

    @newspaper_ns.doc(parser=paper_model, description="Update a newspaper")
    @newspaper_ns.expect(paper_model, validate=True)
    @newspaper_ns.marshal_with(paper_model, envelope='newspaper')
    def post(self, paper_id):
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")
        updated_paper = Newspaper(paper_id=paper_id,
                                  name=newspaper_ns.payload['name'],
                                  frequency=newspaper_ns.payload['frequency'],
                                  price=newspaper_ns.payload['price'])
        return Agency.get_instance().update_newspaper(targeted_paper, updated_paper)

    @newspaper_ns.doc(description="Delete a new newspaper")
    def delete(self, paper_id):
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            return jsonify(f"Newspaper with ID {paper_id} was not found")
        Agency.get_instance().remove_newspaper(targeted_paper)
        return jsonify(f"Newspaper with ID {paper_id} was removed")


@newspaper_ns.route('/<int:paper_id>/issue')
class NewspaperIssue(Resource):
    @newspaper_ns.doc(description="Get all paper issues")
    @newspaper_ns.marshal_list_with(issue_model, envelope='issues')
    def get(self, paper_id):
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")
        return Agency.get_instance().all_issues(targeted_paper)

    @newspaper_ns.doc(description="Create a new paper issue")
    @newspaper_ns.expect(issue_model, validate=True)
    @newspaper_ns.marshal_with(issue_model, envelope='issue')
    def post(self, paper_id):
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")

        # creating a unique ID (optional: customised if not jet existing)
        issue_id = newspaper_ns.payload['issue_id']
        IDs = [x.issue_id for x in targeted_paper.issues]
        while True:
            if issue_id not in IDs:
                break
            issue_id += 1

        # create a new issue object and add it
        new_issue = Issue(issue_id=issue_id,
                          releasedate=newspaper_ns.payload['releasedate'],
                          released=False,  # Initially, paper issues are not published
                          editor_id=newspaper_ns.payload['editor_id'],
                          pages=newspaper_ns.payload['pages'],
                          newspaper_id=paper_id)
        return Agency.get_instance().add_issue(targeted_paper, new_issue)


@newspaper_ns.route("/<int:paper_id>/issue/<int:issue_id>")
class NewspaperIssueID(Resource):
    @newspaper_ns.doc(description="Get information of a specific paper issue")
    @newspaper_ns.marshal_with(issue_model, envelope='issue')
    def get(self, paper_id, issue_id):
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")
        issue = Agency.get_instance().get_issue(targeted_paper, issue_id)
        if not issue:
            abort(404, f"Issue with ID {issue_id} was not found")
        return issue

    @newspaper_ns.doc(description="Update a issue")
    @newspaper_ns.expect(issue_model, validate=True)
    @newspaper_ns.marshal_with(issue_model, envelope='issue')
    def post(self, paper_id, issue_id):
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")  # does not work because it expects to send the aper_model?
        issue = Agency.get_instance().get_issue(targeted_paper, issue_id)
        if not issue:
            abort(404, f"Issue with ID {issue_id} was not found")

        updated_issue = Issue(issue_id=issue_id,
                              releasedate=newspaper_ns.payload['releasedate'],
                              released=issue.released,  # can't undo a release, therefore status can't be changed
                              editor_id=newspaper_ns.payload['editor_id'],
                              pages=newspaper_ns.payload['pages'],
                              newspaper_id=issue.newspaper_id)
        update = Agency.get_instance().update_issue(targeted_paper, issue, updated_issue)
        return update

    @newspaper_ns.doc(description="Delete a issue")
    def delete(self, paper_id, issue_id):
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")
        issue = Agency.get_instance().get_issue(targeted_paper, issue_id)
        if not issue:
            abort(404, f"Issue with ID {issue_id} was not found")
        return Agency.get_instance().remove_issue(targeted_paper, issue)


@newspaper_ns.route("/<int:paper_id>/issue/<int:issue_id>/release")
class NewspaperIssueIDRelease(Resource):
    @newspaper_ns.doc(description="Release an issue")
    @newspaper_ns.marshal_with(issue_model, envelope='issue')
    def post(self, paper_id, issue_id):
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")
        issue = Agency.get_instance().get_issue(targeted_paper, issue_id)
        if not issue:
            abort(404, f"Issue with ID {issue_id} was not found")
        updated_issue = Agency.get_instance().release_issue(issue)
        return updated_issue


@newspaper_ns.route("/<int:paper_id>/issue/<int:issue_id>/editor")
class NewspaperIssueIDEditor(Resource):
    @newspaper_ns.doc(description="Specify an editor for an issue")
    @newspaper_ns.expect(ID_model, validate=True)
    @newspaper_ns.marshal_with(issue_model, envelope='issue')
    def post(self, paper_id, issue_id):
        editor_id = newspaper_ns.payload['ID']
        editor = Agency.get_instance().get_editor(editor_id)
        if not editor:
            abort(404, f"Editor with ID {editor_id} was not found")
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")
        issue = Agency.get_instance().get_issue(targeted_paper, issue_id)
        if not issue:
            abort(404, f"Issue with ID {issue_id} was not found")
        updated_issue = Agency.get_instance().add_editor_to_issue(issue, editor)
        return updated_issue


@newspaper_ns.route("/<int:paper_id>/issue/<int:issue_id>/deliver")
class NewspaperIssueIDDeliver(Resource):
    @newspaper_ns.doc(description="Deliver an issue to a subscriber")
    @newspaper_ns.expect(ID_model, validate=True)
    def post(self, paper_id, issue_id):
        subscriber_id = newspaper_ns.payload['ID']
        subscriber = Agency.get_instance().get_subscriber(subscriber_id)
        if not subscriber:
            abort(404, f"Subscriber with ID {subscriber_id} was not found")
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")
        issue = Agency.get_instance().get_issue(targeted_paper, issue_id)
        if not issue:
            abort(404, f"Issue with ID {issue_id} was not found")
        deliver = Agency.get_instance().deliver_issue(subscriber, issue, targeted_paper)
        return deliver


@newspaper_ns.route('/<int:paper_id>/stats')
class NewspaperStatsID(Resource):
    @newspaper_ns.doc(description="Get information of a specific newspaper")
    def get(self, paper_id):
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")
        info = Agency.get_instance().newspaper_stats(targeted_paper)
        return info




