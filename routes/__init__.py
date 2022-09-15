from api.server.server import Index
from api.emvoip.voice_communication_api import Voice, TwilioToken
from api.emvoip.external_number import RequestCountriesForExternalNumber
from api.emvoip.phone import PhoneRequestCountries, PhoneRequestPricing, PhoneDetail
from api.common.user_api import AllowLogin


from .restx_loader import ns
# ------------ restx resources ------------

#index
ns.add_resource(Index, '/')
# -- end of index route

#twilio token
ns.add_resource(TwilioToken, '/twilio/token')
# -- end of twilio token routes

#login - api access for authorization header
ns.add_resource(AllowLogin, '/login')

#voice twiml
ns.add_resource(Voice, '/voice')
# -- end of voice twiml routes

#external number routes
ns.add_resource(RequestCountriesForExternalNumber,'/ext/countries')
# --- end of external number routes

#phone detailing
ns.add_resource(PhoneRequestCountries, '/countries')
ns.add_resource(PhoneRequestPricing, '/pricing')
ns.add_resource(PhoneDetail, '/number')
# --- end of phone detailing routes




