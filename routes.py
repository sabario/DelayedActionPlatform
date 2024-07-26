from flask import Blueprint, request, jsonify
import os
from your_action_controller import ActionController

FLASK_PORT = os.getenv('FLASK_PORT', 5000)

actions_bp = Blueprint('actions', __name__)

action_controller = ActionController()

@actions_filter_bp.route('/actions', methods=['POST'])
def create_action():
    data = request.json
    return action_controller.create_action(data)

@actions_filter_bp.route('/actions/<action_id>', methods=['PUT'])
def update_action(action_id):
    data = request.json
    return action_controller.update_action(action_id, data)

@actions_filter_bp.route('/actions/<action_id>', methods=['DELETE'])
def delete_action(action_id):
    return action_controller.delete_action(action_id)

@actions_filter_bp.route('/actions/<action_id>', methods=['GET'])
def get_action(action_id):
    return action_controller.get_action(action_id)

@actions_filter_bp.route('/actions', methods=['GET'])
def list_actions():
    return action_controller.list_actions()