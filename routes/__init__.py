from api.common.server import Index
from api.common.communication_api import Voice, TwilioToken
from api.common.external_number import RequestCountriesForExternalNumber
from api.common.phone import PhoneRequestCountries, PhoneRequestPricing, PhoneDetail

from .restx_loader import ns
# ------------ restx resources ------------

#index
ns.add_resource(Index, '/')
# -- end of index route

#twilio token
ns.add_resource(TwilioToken, '/twilio/token')
# -- end of twilio token routes

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




