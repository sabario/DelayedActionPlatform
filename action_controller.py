from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from celery import Celery
import os
from dotenv import load_dotenv
import logging

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['result_backend'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

db = SQLAlchemy(app)

auth = HTTPBasicAuth()
users = {
    os.getenv('ADMIN_USER'): generate_password_hash(os.getenv('ADMIN_PASSWORD'))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

logging.basicConfig(level=logging.INFO)

class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    delay = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

@celery.task
def perform_action(action_id):
    action = Action.query.filter_by(id=action_id).first()
    if action:
        logging.info(f"Performing action {action.name} with delay of {action.delay} seconds.")
        return True
    return False

def add_action(name, delay):
    new_action = Action(name=name, delay=delay)
    db.session.add(new_action)
    db.session.commit()
    logging.info(f"Added action {new_action.name} with ID {new_action.id}")

    perform_action.apply_async((new_action.id,), countdown=delay)

    return new_action.id

@app.route('/actions', methods=['POST'])
@auth.login_required
def create_action():
    pass
    
@app.route('/actions/<int:action_id>', methods=['GET'])
@auth.login_required
def retrieve_action(action_id):
    pass

if __name__ == '__main__':
    app.run(debug=True)