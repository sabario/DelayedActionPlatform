from flask import Blueprint, request, jsonify, make_response
import os
from your_action_controller import ActionController

FLASK_PORT = os.getenv('FLASK_PORT', 5000)

actions_bp = Blueprint('actions', __name__)

action_controller = ActionController()

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@actions_bp.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@actions_bp.route('/actions', methods=['POST'])
def create_action():
    data = request.json
    try:
        return action_controller.create_action(data), 201
    except Exception as e:
        raise InvalidUsage(f"Error creating action: {str(e)}", status_code=400)

@actions_bp.route('/actions/<action_id>', methods=['PUT'])
def update_action(action_id):
    data = request.json
    try:
        return action_controller.update_action(action_id, data)
    except KeyError:
        raise InvalidUsage('Action not found', status_code=404)
    except Exception as e:
        raise InvalidUsage(f"Error updating action: {str(e)}", status_code=400)

@actions_bp.route('/actions/<action_id>', methods=['DELETE'])
def delete_action(action_id):
    try:
        return action_controller.delete_action(action_id)
    except KeyError:
        raise InvalidUsage('Action not found', status_code=404)
    except Exception as e:
        raise InvalidUsage(f"Error deleting action: {str(e)}", status_code=400)

@actions_bp.route('/actions/<action_id>', methods=['GET'])
def get_action(action_id):
    try:
        return action_controller.get_action(action_id)
    except KeyError:
        raise InvalidUsage('Action not found', status_code=404)
    except Exception as e:
        raise InvalidUsage(f"Error retrieving action: {str(e)}", status_code=400)

@actions_bp.route('/actions', methods=['GET'])
def list_actions():
    try:
        return action_controller.list_actions()
    except Exception as e:
        raise InvalidUsage(f"Error listing actions: {str(e)}", status_code=500)