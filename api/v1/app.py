from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from api.v1.views import app_views
from flask_swagger_ui import get_swaggerui_blueprint
from models.user import User
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.register_blueprint(app_views)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
CORS(app, supports_credentials=True, resources={
     r"/api/v1/*": {"origins": "http://127.0.0.1:5000"}})


SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "DigiBank API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()


@app.errorhandler(404)
def error_handler(e):
    return {"error": "No Data found"}, 404


if __name__ == "__main__":
    host = "0.0.0.0"
    app.run(debug=True, host=host, port=5001, threaded=True)
