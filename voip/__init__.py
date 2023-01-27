from flask import Flask

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

from flask_restx import Api

from config import Config
from .__version__ import version

from routes.restx_loader import restx_api
from flask_bcrypt import Bcrypt

from dotenv import load_dotenv
import os


cors = CORS(origins=os.getenv('AllOWED_ORIGINS_CORS'))
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins=os.getenv('ALLOWED_ORIGINS_SOCKET'))
bcrpyt = Bcrypt()



def create_app(config_class=Config):
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


    return app