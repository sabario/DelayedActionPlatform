from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.before_request
def log_request_info():
    if request.is_json:
        app.logger.debug('JSON Request: %s', request.get_json())
    else:
        app.logger.debug('Non-JSON Request received')

@app.route('/delayed-action', methods=['POST'])
def handle_delayed_action():
    data = request.get_json()
    return jsonify({"status": "success", "received_data": data}), 200

if __name__ == '__main__':
    app_port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=app_port)