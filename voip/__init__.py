from flask import Flask

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

from flask_restx import Api

from config import Config
from .__version__ import version


from routes.ret import restx_api


api = Api(version=f'{version}', title='VOIP API')
cors = CORS()
jwt = JWTManager()
socketio = SocketIO()



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #initialize packages
    cors.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)
    # api.init_app(app)
    restx_api.init_app(app)


    return app