from flask import Blueprint, request, jsonify, make_response
import os
from your_action_controller import ActionController

SERVER_PORT = os.getenv('FLASK_PORT', 5000)

action_blueprint = Blueprint('actions_endpoint', __name__)

action_manager = ActionController()

class APIUsageError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        return {'message': self.message, **self.payload}

@action_blueprint.errorhandler(APIUsageError)
def handle_api_usage_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def execute_action_based_on_method(action_id=None, operation=None):
    try:
        action_data = request.json if request.json is not None else {}
        if operation == 'create':
            created_action = action_manager.create_action(action_data)
            return jsonify(created_action), 201
        elif operation == 'update':
            updated_action = action_manager.update_action(action_id, action_data)
            return jsonify(updated_action)
        elif operation == 'delete':
           deleted_status = action_manager.delete_action(action_id)
           return jsonify(deleted_status)
        elif operation == 'get':
            action_details = action_manager.get_action(action_id)
            return jsonify(action_details)
    except KeyError:
        raise APIUsageError('Action not found', status_code=404)
    except Exception as exc:
        if operation in ['create', 'update']:
            error_status_code = 400
        else:
            error_status_code = 500
        raise APIUsageError(f"Error processing action ({operation}): {str(exc)}", status_code=error_status_code)

@action_blueprint.route('/actions', methods=['POST'])
def create_action_endpoint():
    return execute_action_based_on_method(operation='create')

@action_blueprint.route('/actions/<action_id>', methods=['PUT'])
def update_action_endpoint(action_id):
    return execute_action_based_on_method(action_id=action_id, operation='update')

@action_blueprint.route('/actions/<action_id>', methods=['DELETE'])
def delete_action_endpoint(action_id):
    return execute_action_based_on_method(action_id=action_id, operation='delete')

@action_blueprint.route('/actions/<action_id>', methods=['GET'])
def get_action_endpoint(action_id):
    return execute_action_based_on_method(action_id=action_id, operation='get')

@action_blueprint.route('/actions', methods=['GET'])
def list_all_actions_endpoint():
    try:
        all_actions = action_manager.list_actions()
        return jsonify(all_actions)
    except Exception as exc:
        raise APIUsageError(f"Error retrieving list of actions: {str(exc)}", status_code=500)