from flask import jsonify
from flask_restx import Namespace, reqparse, Resource, fields, abort

from ..model.agency import Agency
from ..model.subscriber import Subscriber

subscriber_ns = Namespace("subscriber", description="Subscriber related operations")

subscriber_model = subscriber_ns.model('SubscriberModel', {
    'ID': fields.Integer(required=False,
                         help='The unique identifier of a subscriber'),
    'name': fields.String(required=True,
                          help='The name of the subscriber'),
    'address': fields.String(required=True,
                             help='The address of the subscriber')
   })

newspaperID_model = subscriber_ns.model('NewspaperIDModel', {
    'paper_id': fields.Integer(required=True,
                               help='The unique identifier of a newspaper')
})


@subscriber_ns.route('/')
class SubscriberAPI(Resource):
    @subscriber_ns.doc(subscriber_model, description="Add a new subscriber")
    @subscriber_ns.expect(subscriber_model, validate=True)
    @subscriber_ns.marshal_with(subscriber_model, envelope='subscriber')
    def post(self):
        # create a unique ID (optional: customised ID if not yet existing)
        subscriber_id = subscriber_ns.payload['ID']
        IDs = [x.ID for x in Agency.get_instance().subscribers]
        while True:
            if subscriber_id not in IDs:
                break
            subscriber_id += 1
        # create a new subscriber object and add it
        new_subscriber = Subscriber(ID=subscriber_id,
                                    name=subscriber_ns.payload['name'],
                                    address=subscriber_ns.payload['address'])
        return Agency.get_instance().add_subscriber(new_subscriber)

    @subscriber_ns.doc(description="List all subscribers")
    @subscriber_ns.marshal_list_with(subscriber_model, envelope='subscriber')
    def get(self):
        return Agency.get_instance().all_subscribers()


@subscriber_ns.route('/<int:subscriber_id>')
class SubscriberID(Resource):
    @subscriber_ns.doc(description="Get an subscribers information")
    @subscriber_ns.marshal_with(subscriber_model, envelope='subscriber')
    def get(self, subscriber_id):
        subscriber = Agency.get_instance().get_subscriber(subscriber_id)
        return subscriber

    @subscriber_ns.doc(parser=subscriber_model, description="Update an subscribers information")
    @subscriber_ns.expect(subscriber_model, validate=True)
    @subscriber_ns.marshal_with(subscriber_model, envelope='subscriber')
    def post(self, subscriber_id):
        targeted_subscriber = Agency.get_instance().get_subscriber(subscriber_id)
        if not targeted_subscriber:
            abort(404, f"Subscriber with ID {subscriber_id} was not found")
        updated_subscriber = Subscriber(ID=subscriber_id,
                                        name=subscriber_ns.payload['name'],
                                        address=subscriber_ns.payload['address'])
        return Agency.get_instance().update_subscriber(targeted_subscriber, updated_subscriber)

    @subscriber_ns.doc(description="Delete an subscriber")
    def delete(self, subscriber_id):
        targeted_subscriber = Agency.get_instance().get_subscriber(subscriber_id)
        if not targeted_subscriber:
            return jsonify(f"Subscriber with ID {subscriber_id} was not found")
        Agency.get_instance().remove_subscriber(targeted_subscriber)
        return jsonify(f"Subscriber with ID {subscriber_id} was removed")


@subscriber_ns.route('/<int:subscriber_id>/subscribe')
class SubscriberIDSubscribe(Resource):
    @subscriber_ns.doc(newspaperID_model, description="Subscribe a subscriber to a newspaper")
    @subscriber_ns.expect(newspaperID_model, validate=True)
    def post(self, subscriber_id):
        paper_id = subscriber_ns.payload['paper_id']
        targeted_paper = Agency.get_instance().get_newspaper(paper_id)
        if not targeted_paper:
            abort(404, f"Newspaper with ID {paper_id} was not found")
        subscriber = Agency.get_instance().get_subscriber(subscriber_id)
        if not subscriber:
            abort(404, f"Subscriber with ID {subscriber_id} was not found")
        return Agency.get_instance().subscribe_to_paper(subscriber, targeted_paper)


@subscriber_ns.route('/<int:subscriber_id>/stats')
class SubscriberIDStats(Resource):
    @subscriber_ns.doc(description="Get the number of newspaper subscriptions and details")
    def get(self, subscriber_id):
        subscriber = Agency.get_instance().get_subscriber(subscriber_id)
        if not subscriber:
            abort(404, f"Subscriber with ID {subscriber_id} was not found")
        info = Agency.get_instance().get_subscriber_stats(subscriber)
        return info


@subscriber_ns.route('/<int:subscriber_id>/missingissues')
class SubscriberIDMissingIssues(Resource):
    @subscriber_ns.doc(description="Check for undelivered issues of the subscribed newspapers")
    def get(self, subscriber_id):
        subscriber = Agency.get_instance().get_subscriber(subscriber_id)
        if not subscriber:
            abort(404, f"Subscriber with ID {subscriber_id} was not found")
        missing = Agency.get_instance().check_missingissues(subscriber)
        return jsonify(missing)
