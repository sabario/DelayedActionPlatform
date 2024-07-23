from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from datetime import timedelta
from functools import update_wrapper
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

CACHE = {}
CACHE_TIMEOUT = 300

def cache_response(f):
    def decorator(*args, **kwargs):
        key = (request.path, frozenset(request.args.items()), frozenset(request.get_json().items()) if request.is_json else None)
        if key in CACHE:
            cache_entry = CACHE[key]
            if cache_entry['timestamp'] + CACHE_TIMEOUT > app.current_time():
                return cache_entry['response']
        result = f(*args, **kwargs)
        CACHE[key] = {'timestamp': app.current_time(), 'response': result}
        return result
    return update_wrapper(decorator, f)

@app.before_request
def log_request_info():
    if request.is_json:
        app.logger.debug('JSON Request: %s', request.get_json())
    else:
        app.logger.debug('Non-JSON Request received')

@app.route('/delayed-action', methods=['POST'])
@cache_response
def handle_delayed_action():
    data = request.get_json()
    return jsonify({"status": "success", "received_data": data}), 200

app.current_time = staticmethod(lambda: int(time.time()))

if __name__ == '__main__':
    app_port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=app_port)