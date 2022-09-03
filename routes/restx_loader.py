from flask_restx import Api

restx_api = Api()

ns = restx_api.namespace('voip', description='Voice Over Internet Protocols')
