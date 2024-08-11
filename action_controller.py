from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import logging

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define the Action model
class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    delay = db.Column(db.Integer, nullable=False)  # Delay in seconds

# Create table(s)
with app.app_context():
    db.create_all()

# Function to add a new action with log
def add_action(name, delay):
    new_action = Action(name=name, delay=delay)
    db.session.add(new_action)
    db.session.commit()
    logging.info(f"Added action {new_action.name} with ID {new_action.id}")
    return new_action.id

# Function to get an action by id with log
def get_action(action_id):
    action = Action.query.filter_by(id=action_id).first()
    if action:
        logging.info(f"Retrieved action {action.name} with ID {action.id}")
        return {'id': action.id, 'name': action.name, 'delay': action.delay}
    else:
        logging.warning(f"Action with ID {action_id} not found")
        return None

# Function to update an existing action with log
def update_action(action_id, name=None, delay=None):
    action = Action.query.get(action_id)
    if action:
        if name:
            action.name = name
        if delay:
            action.delay = delay
        db.session.commit()
        logging.info(f"Updated action ID {action_id}")
        return True
    else:
        logging.warning(f"Failed to update; action ID {action_id} not found")
        return False

# Function to delete an action with log
def delete_action(action_id):
    action = Action.query.get(action_id)
    if action:
        db.session.delete(action)
        db.session.commit()
        logging.info(f"Deleted action ID {action_id}")
        return True
    else:
        logging.warning(f"Failed to delete; action ID {action_id} not found")
        return False

# Controller functions exposed through API endpoints
@app.route('/actions', methods=['POST'])
def create_action():
    data = request.get_json()
    action_id = add_action(data['name'], data['delay'])
    return jsonify({'message': 'Action added', 'action_id': action_id}), 201

@app.route('/actions/<int:action_id>', methods=['GET'])
def retrieve_action(action_id):
    action = get_action(action_id)
    if action:
        return jsonify({'action': action}), 200
    else:
        return jsonify({'message': 'Action not found'}), 404

@app.route('/actions/<int:action_id>', methods=['PUT'])
def edit_action(action_id):
    data = request.get_json()
    result = update_action(action_id, data.get('name'), data.get('delay'))
    if result:
        return jsonify({'message': 'Action updated successfully'}), 200
    else:
        return jsonify({'message': 'Action not found'}), 404

@app.route('/actions/<int:action_id>', methods=['DELETE'])
def remove_action(action_id):
    if delete_action(action_id):
        return jsonify({'message': 'Action deleted successfully'}), 200
    else:
        return jsonify({'message': 'Action not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)