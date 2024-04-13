from flask import jsonify
from flask_restx import Namespace, reqparse, Resource, fields, abort

from ..model.agency import Agency
from ..model.editor import Editor
from .newspaperNS import issue_model

editor_ns = Namespace("editor", description="Editor related operations")


editor_model = editor_ns.model('EditorModel', {
    'ID': fields.Integer(required=False,
                         help='The unique identifier of a editor'),
    'name': fields.String(required=True,
                          help='The name of the editor'),
    'address': fields.String(required=True,
                             help='The address of the editor'),
   })


@editor_ns.route('/')
class EditorAPI(Resource):
    @editor_ns.doc(editor_model, description="Add a new editor")
    @editor_ns.expect(editor_model, validate=True)
    @editor_ns.marshal_with(editor_model, envelope='editor')
    def post(self):
        # create a unique ID (optional: customised ID if not yet existing)
        editor_id = editor_ns.payload['ID']
        IDs = [x.ID for x in Agency.get_instance().editors]
        while True:
            if editor_id not in IDs:
                break
            editor_id += 1
        # create a new editor object and add it
        new_editor = Editor(ID=editor_id,
                            name=editor_ns.payload['name'],
                            address=editor_ns.payload['address'])
        return Agency.get_instance().add_editor(new_editor)

    @editor_ns.doc(description="List all editors")
    @editor_ns.marshal_list_with(editor_model, envelope='editor')
    def get(self):
        return Agency.get_instance().all_editors()


@editor_ns.route('/<int:editor_id>')
class EditorID(Resource):
    @editor_ns.doc(description="Get an editors information")
    @editor_ns.marshal_with(editor_model, envelope='editor')
    def get(self, editor_id):
        editor = Agency.get_instance().get_editor(editor_id)
        return editor

    @editor_ns.doc(parser=editor_model, description="Update an editors information")
    @editor_ns.expect(editor_model, validate=True)
    @editor_ns.marshal_with(editor_model, envelope='editor')
    def post(self, editor_id):
        targeted_editor = Agency.get_instance().get_editor(editor_id)
        if not targeted_editor:
            abort(404, f"Editor with ID {editor_id} was not found")
        updated_editor = Editor(ID=editor_id,
                                name=editor_ns.payload['name'],
                                address=editor_ns.payload['address'])
        return Agency.get_instance().update_editor(targeted_editor, updated_editor)

    @editor_ns.doc(description="Delete an editor")
    def delete(self, editor_id):
        targeted_editor = Agency.get_instance().get_editor(editor_id)
        if not targeted_editor:
            return jsonify(f"Editor with ID {editor_id} was not found")
        Agency.get_instance().remove_editor(targeted_editor)
        return jsonify(f"Editor with ID {editor_id} was removed")


@editor_ns.route('/<int:editor_id>/issues')
class EditorIssues(Resource):
    @editor_ns.doc(description="Get newspaper issues that a editor is responsible for")
    @editor_ns.marshal_list_with(issue_model, envelope='editor')
    def get(self, editor_id):
        targeted_editor = Agency.get_instance().get_editor(editor_id)
        if not targeted_editor:
            abort(404, f"Editor with ID {editor_id} was not found")
        issues = Agency.get_instance().get_editor_issues(targeted_editor)
        return issues


