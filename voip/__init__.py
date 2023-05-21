from flask import Flask

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

from config import Config
from .__version__ import version

from routes.restx_loader import restx_api
from flask_bcrypt import Bcrypt

from dotenv import load_dotenv
import os



origins_cors = os.getenv('AllOWED_ORIGINS_CORS')

cors = CORS(resources={r"/*": {"origins": f"{origins_cors}"}})
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins=os.getenv('ALLOWED_ORIGINS_SOCKET'))
bcrpyt = Bcrypt()



def create_app(config_class=Config, settings_override=None):
    app = Flask(__name__, template_folder='templates', static_folder='staticFiles')
    app.config.from_object(config_class)
    app.config['CORS_HEADERS'] = 'application/json'

    #initialize packages
    cors.init_app(app)
    socketio.init_app(app)
    # api.init_app(app)
    restx_api.init_app(app)
    jwt.init_app(app)
    bcrpyt.init_app(app)
    # api.init_app(app)

    if settings_override:
        app.config.update(settings_override)


    return app