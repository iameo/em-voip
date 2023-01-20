from api.server.server import Index
from api.emvoip.voice_communication_api import EndCall, HandleCall, Voice, TwilioToken
from api.emvoip.sms import SendSMS
from api.emvoip.external_number import RequestCountriesForExternalNumber
from api.emvoip.phone import PhoneRequestCountries, PhoneRequestPricing, PhoneDetail, PurchasedNumbers
from api.common.user_api import AllowLogin, AllowRegister
from api.server.server import Twilio


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

ns.add_resource(AllowRegister, '/register')

#voice twiml - initiates calling system
ns.add_resource(Voice, '/voice')

#handle call
ns.add_resource(HandleCall, '/call/handle')

#end call
ns.add_resource(EndCall, '/call/end')


# -- end of voice twiml routes



# --- start of sms routes
ns.add_resource(SendSMS, '/sms/send')

# --- end of sms routes


#external number routes
ns.add_resource(RequestCountriesForExternalNumber,'/ext/countries')
# --- end of external number routes

#phone detailing
ns.add_resource(PhoneRequestCountries, '/countries')
ns.add_resource(PhoneRequestPricing, '/pricing')
ns.add_resource(PhoneDetail, '/number')
ns.add_resource(PurchasedNumbers, '/purchased/numbers')
# --- end of phone detailing routes


#index
ns.add_resource(Twilio, '/voip_home', endpoint='love')



