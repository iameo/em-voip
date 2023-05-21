from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException, TwilioRestException
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
from utils.exts import get_db_data_by_query
from utils.auth import auth_checker
from db import db_fetch, db_id_maker, post_data_to_db, db_save
from datetime import datetime
from model.response import response_model

import os
from dotenv import load_dotenv

load_dotenv()




main_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
main_account_auth_token = os.getenv('TWILIO_AUTH_TOKEN')


Client = TwilioClient(main_account_sid, main_account_auth_token)

#------ index for db hits and saves
phone_index = 'phone_repo'
SUBACCOUNT_INDEX = os.getenv('SUBACCOUNT_INDEX', 'subaccountz')

class Phone(object):
    @auth_checker
    #this should be for the logged individual
    def purchased_numbers(self, n=None, account_id=None):
        try:
            n = int(n)
        except (ValueError, TypeError):
            n = None

        account = get_db_data_by_query(index=f'{SUBACCOUNT_INDEX}', search_parameter={"account_id":account_id})
        if account:
            subclient = TwilioClient(account['twilio_account_sid'], account['twilio_auth_token'])
        else:
            return {"msg": "you are yet to subscribe to a plan"}

        numbers = subclient.incoming_phone_numbers.list(limit=n)
        return {'numbers': c.phone_number for c in numbers} if numbers else {"numbers": []}


    @auth_checker
    def request_countries(self):
        countries = Client.available_phone_numbers.list()

        all_countries = {}
        for country in countries:
            all_countries.update({
                country.country: country.country_code
            })
        all_countries = dict(sorted(all_countries.items()))

        all_countries_with_code = {}
        for country, code in all_countries.items():
            for _code, iso in COUNTRY_CODE_TO_REGION_CODE.items():
                iso = ''.join(iso[0])
                if code == iso:
                    country = f"{country} (+{str(_code)})"
                    all_countries_with_code.update({country:code})
        _all_countries_with_code = {y:x for x,y in all_countries_with_code.items()}

        return _all_countries_with_code

    @auth_checker
    def request_number_pricing(self, country):
        price = Client.pricing.v1.phone_numbers.countries(str(country)).fetch()

        details = list()
        if price:
            details.append({
                'country': country,
                "prices": price.phone_number_prices,
                "price_unit": price.price_unit
            })
            return {'data':details, 'status':200}
        return {'data': {}, 'status': 400}


    def allocate_number(self, area_code, country, user_id, account_id):
        """
        Buy phone number and allocate twilio twiml url for voice calls
        """
        account = get_db_data_by_query(index=f'{SUBACCOUNT_INDEX}', search_parameter={"account_id":account_id})

        if account:
            account = account
        else:
            _ts = datetime.utcnow()

            try:
                account = Client.api.accounts.create(
                friendly_name=f'{account_id}'
            )
            except TwilioRestException as e:
                return None, None
            except TwilioException as e:
                return None, None
            subaccount_data = {
                "_id": db_id_maker('subaccount'),
                "account_name": account.friendly_name,
                "account_id": account_id,
                "status": 1 if account.status == 'active' else 0,
                "subresource_uris": account.subresource_uris,
                "twilio_status": account.status,
                "type": account.type,
                "uri": account.uri,
                "main_account_sid": account.owner_account_sid,
                "is_archived": 0,
                "is_delete": 0,
                "is_shared": 1,
                "created": _ts,
                "modified": _ts,
                "modified_by": user_id,
                "twilio_account_sid": account.sid,
                "twilio_auth_token": account.auth_token,

            }

            #save to db
            post_data_to_db(index="subaccountsx", json_data=subaccount_data)
            account = {"twilio_account_sid": subaccount_data['twilio_account_sid'], 'twilio_auth_token': subaccount_data['twilio_auth_token']}
        
        subclient = TwilioClient(account['twilio_account_sid'], account['twilio_auth_token'])


        if country and area_code:
            record = subclient.available_phone_numbers(country).local.list(area_code=area_code, limit=1)

        if country and not area_code:
            record = subclient.available_phone_numbers(country).local.list(limit=1)
        
        try:
            _record = record[0]
        except (IndexError, KeyError, TypeError):
            return None, subclient

        capabilities = _record.capabilities
        number_data = {
            "address_requirements": _record.address_requirements,
            "capabilities": {
                "mms": capabilities['MMS'],
                "sms": capabilities['SMS'],
                "voice": capabilities['voice']
            },
            "phone_number": _record.phone_number,
            "is_shared": 1
        }
        return number_data, subclient


    def new_phone_detail(self, json_data: dict = None, account_id: str = None, user_id: str = None):
        try:
            phone_record, subclient = self.allocate_number(area_code=json_data['area_code'], country=json_data['country'],\
            account_id=account_id, user_id=user_id)
        except TypeError:
            return {'message': 'something went wrong.', 'status': 500, 'data': {}}
        if phone_record is None:
            return {'status':503, 'message': 'we could not allocate a phone number at this time.'}
   
        json_data.update(phone_record)
        address_requirement = phone_record.get('address_requirements')
        if address_requirement == 'none':
            phone_status = self.instant_number_allocation(json_data=json_data, account_id=account_id, user_id=user_id, twilio_client=subclient)
        
        else: #any, local, foreign
            message = f"A {address_requirement} address in {json_data['country']} is required."
            phone_status = None #todo
            return {'message': message, 'data':{}}
        return phone_status


    def instant_number_allocation(self, json_data=None, account_id=None, user_id=None, twilio_client=None):
        label = 'Personal Number'
        
        primary_number_availablity = db_fetch(index=phone_index, query={
            'query': {
                'bool': {
                    'must': [
                        {
                            'match_phrase': {
                                'is_primary': 1
                            }
                        },
                        {
                            'match_phrase': {
                                'user_id': user_id
                            }
                        },
                        {
                            'match_phrase': {
                                'is_delete': 0
                            }
                        }
                    ]
                }
            }
        })

        if primary_number_availablity:
            json_data['is_primary'] = 0
        else:
            json_data['is_primary'] = 1

        if json_data['is_shared'] == 1:
            label = 'Group Number'
            json_data['members'] = []

        twiml_app_sid = self.twiml_sid(twilio_client, account_id)

        try:
            number_provision = twilio_client.incoming_phone_numbers.create(
            phone_number=json_data.get('phone_number'),
            voice_application_sid=str(twiml_app_sid)
        )
        except (TwilioException, TwilioRestException) as e:
            return {"msg": str(e)}

        json_data.update({
            "label": f"{json_data['country']} | {label}",
            "phone_number_sid": number_provision.sid,
            "forwarding_enabled": 0,
            "forward_to": '',
            "voice_greeting_enabled": 0,
            "voice_greeting_url": ''
        })

        data = db_save(index=phone_index, json_data=json_data, account_id=account_id, user_id=user_id)
        if not data:
            return {'status':500, 'message': 'we could not provision a phone number for you at this time.'}
        return {'status': 201, 'data':data, 'message': 'new phone number provisioned.'}


    def add_address(self, json_data=None, account_id=None):
        '''
        To meet Regulatory notice for countries that request a local address\
        before twilio number can be purchased
        '''
        account = get_db_data_by_query(index="subaccounts", search_parameter={"account_id":account_id})

        if not account:
            return {"message":"account do not owe a number to assign this address to"} #base response - not bad

        #initialize twilio client
        twilio_client = TwilioClient(account['twilio_account_sid'], account['twilio_auth_token'])
        
        try:
            address_details = twilio_client.addresses.create(
                customer_name=json_data['customer_name'],
                street=json_data['street'],
                city=json_data['city'],
                region=json_data['region'],
                postal_code=json_data['postal_code'],
                iso_country=json_data['country'] #iso
        )

        except (TwilioException, TwilioRestException) as e:
            return {"message": str(e)}

        return {
            "dependent_phone_numbers": address_details.dependent_phone_numbers.list(), 
            "emergency_enabled": address_details.emergency_enabled,
            "validated": address_details.validated, #false
            "verified": address_details.verified #false
        }


    def addresses(self, account_id):
        account = get_db_data_by_query(index="subaccounts", search_parameter={"account_id":account_id})

        if not account:
            return {"msg":"you do not have an active account yet. kindly purchase a phone number"}

        twilio_client = TwilioClient(account['twilio_account_sid'], account['twilio_auth_token'])
        addresses = twilio_client.addresses.list()
    
        data = {
            "validated": [address.validated for address in addresses],
            "street": [address.street for address in addresses],
            "verified": [address.verified for address in addresses],
            "customer_name": [address.customer_name for address in addresses],
            }

        return data


    @auth_checker
    def twiml_sid(self, subclient=None, account_id=None):
        applications = subclient.applications.list(friendly_name=f"{account_id}_TWIML_APP", limit=1)
        if not applications:
            application = subclient.applications.create(friendly_name=f"{account_id}_TWIML_APP")
            return application.sid
        return applications[0].sid

        




        
