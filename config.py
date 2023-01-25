from dotenv import load_dotenv
import os

load_dotenv()


class Config(object):
    CLIENT_ID= os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    SECRET_KEY = os.getenv('jwt_key')
    JWT_SECRET_KEY = os.getenv('jwt_key')
    PROPAGATE_EXCEPTIONS = True

    ALLOWED_SOCKET_ORIGINS = "*"
    DEBUG = os.getenv('DEBUG', False)
    JWT_TOKEN_LOCATION = ['headers', 'query_string']

