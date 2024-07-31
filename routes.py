from flask import Blueprint, request, jsonify, make_response
import os
from your_action_controller import ActionController

FLASK_PORT = os.getenv('FLASK_PORT', 5000)

actions_bp = Blueprint('actions', __name__)

action_controller = ActionController()

class InvalidUsage(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        return {'message': self.message, **self.payload}

@actions_bp.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

def process_action_request(action_id=None, method=None):
    try:
        data = request.json if request.json is not None else {}
        if method == 'create':
            return jsonify(action_controller.create_action(data)), 201
        elif method == 'update':
            return jsonify(action_controller.update_action(action_id, data))
        elif method == 'delete':
            return jsonify(action_controller.delete_action(action_id))
        elif method == 'get':
            return jsonify(action_controller.get_action(action_id))
    except KeyError:
        raise InvalidUsage('Action not found', status_code=404)
    except Exception as e:
        if method in ['create', 'update']:
            status_code = 400
        else:
            status_code = 500
        raise InvalidUsage(f"Error {method}ing action: {str(e)}", status_code=status_code)

@actions_bp.route('/actions', methods=['POST'])
def create_action():
    return process_action_request(method='create')

@actions_bp.route('/actions/<action_id>', methods=['PUT'])
def update_action(action_id):
    return process_action_request(action_id=action_id, method='update')

@actions_bp.route('/actions/<action_id>', methods=['DELETE'])
def delete_action(action_id):
    return process_action_request(action_id=action_id, method='delete')

@actions_bp.route('/actions/<action_id>', methods=['GET'])
def get_action(action_id):
    return process_action_request(action_id=action_id, method='get')

@actions_bp.route('/actions', methods=['GET'])
def list_actions():
    try:
        actions_list = action_controller.list_actions()
        return jsonify(actions_list)
    except Exception as e:
        raise InvalidUsage(f"Error listing actions: {str(e)}", status_code=500)