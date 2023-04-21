from flask_restx import Api

restx_api = Api(authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}})

ns = restx_api.namespace('voip', description='Voice Over Internet Protocols \n Register => Login => Enter token as Bearer $token')
