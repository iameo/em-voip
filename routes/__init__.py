#from app_voipp import api
from flask_restx import Api
from api.common.server import Index
from api.common.communication_api import Voice, TwilioToken
from api.common.external_number import RequestCountriesForExternalNumber
from api.common.phone import PhoneRequestCountries, PhoneRequestPricing, PhoneDetail
from services.phone import Phone

restx_api = Api()


# ------------ restx resources ------------

#index
restx_api.add_resource(Index, '/')
# -- end of index route

#twilio token
restx_api.add_resource(TwilioToken, '/twilio/token')
# -- end of twilio token routes

#voice twiml
restx_api.add_resource(Voice, '/voice')
# -- end of voice twiml routes

#external number routes
restx_api.add_resource(RequestCountriesForExternalNumber,'/ext/countries')
# --- end of external number routes

#phone detailing
restx_api.add_resource(PhoneRequestCountries, '/countries')
restx_api.add_resource(PhoneRequestPricing, '/pricing')
restx_api.add_resource(PhoneDetail, '/number')
# --- end of phone detailing routes




