from flask import Flask, request
from flask_cors import CORS
from flask_login import LoginManager
from api.v1.views import app_views
from models.user import User


app = Flask(__name__)
app.secret_key = 'youp'
app.register_blueprint(app_views)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
CORS(app, supports_credentials=True, resources={
     r"/api/v1/*": {"origins": "http://127.0.0.1:5000"}})


@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()


@app.errorhandler(404)
def error_handler(e):
    return {"error": "No Data found"}, 404


if __name__ == "__main__":
    host = "0.0.0.0"
    app.run(debug=True, host=host, port=5001, threaded=True)