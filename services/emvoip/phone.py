from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException, TwilioRestException
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
from utils.exts import get_db_data_by_query
from utils.auth import auth_checker
from db import db_fetch, db_id_maker, post_data_to_db, db_save
from datetime import datetime

import os

main_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
main_account_auth_token = os.getenv('TWILIO_AUTH_TOKEN')


Client = TwilioClient(main_account_sid, main_account_auth_token)

#------ index for db hits and saves
phone_index = 'phone_repo'

class Phone(object):
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


    def allocate_number(self, area_code, country, user_id, company_id):
        """
        Buy phone number and allocate twilio twiml url for voice calls
        """
        account = get_db_data_by_query(index="subaccounts", search_parameter={"company_id":company_id})

        if account:
            account = account[0]
        else:
            _ts = datetime.utcnow()

            account = Client.api.accounts.create(
                friendly_name=str(company_id)
            )
            subaccount_data = {
                "_id": db_id_maker('subaccount'),
                "account_name": account.name,
                "company_id": company_id,
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
            post_data_to_db(index="subaccounts", json_data=subaccount_data)
            account = {"twilio_account_sid": subaccount_data['twilio_account_sid'], 'twilio_auth_token': subaccount_data['twilio_auth_token']}
        
        subclient = TwilioClient(account['twilio_account_sid'], account['twilio_auth_token'])

        if country and area_code:
            record = subclient.available_phone_numbers(country).local.list(area_code=area_code, limit=1)
        
        if country and not area_code:
            record = subclient.available_phone_numbers(country).local.list(limit=1)
        
        try:
            record = record['available_phone_numbers']
            _record = record[0]
        except (IndexError, KeyError):
            return None
        return {
            "address_requirements": _record.get('address_requirements'),
            "capabilities": {
                "mms": _record['capabilities']['mms'],
                "sms": _record['capabilities']['sms'],
                "voice": _record['capabilities']['voice']
            },
            "phone_number": _record.get('phone_number')
        }, subclient


    def new_phone_detail(self, json_data: dict = None, company_id: str = None, user_id: str = None):
        phone_record, subclient = self.allocate_number(area_code=json_data['area_code'], country=json_data['country'],\
            company_id=company_id, user_id=user_id)

        if phone_record is None:
            return {'status':503, 'message': 'we could not allocate a phone number at this time'}
        
        address_requirement = phone_record.get('address_requirements')
        if address_requirement == 'none':
            phone_status = self.instant_number_allocation(json_data=json_data, company_id=company_id, user_id=user_id, twilio_client=subclient)
        
        else: #any, local, foreign
            message = f'Address of type {address_requirement} is required to proceed'
            phone_status = None #todo
        return phone_status


    def instant_number_allocation(self, json_data=None, company_id=None, user_id=None, twilio_client=None):
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

        twiml_app_sid = self.twiml_sid(twilio_client, company_id)

        number_provision = twilio_client.incoming_phone_numbers.create(
            phone_number=json_data.get('phone_number'),
            voice_application_sid=str(twiml_app_sid)
        )

        json_data.update({
            "label": f"{json_data['country']} | {label}",
            "phone_number_sid": number_provision.sid,
            "forwarding_enabled": 0,
            "forward_to": '',
            "voice_greeting_enabled": 0,
            "voice_greeting_url": ''
        })

        data = db_save(index=phone_index, json_data=json_data, company_id=company_id, user_id=user_id)
        if not data:
            return {'status':500, 'messgae': 'we could not provision a phone number for you at this time.'}
        return {'status': 201, 'data':data, 'message': 'new phone number provisioned.'}


    @property
    def twiml_sid(self, subclient=None, company_id=None):
        applications = subclient.applications.list(friendly_name=f"{company_id}_TWIML_APP", limit=1)
        if not applications:
            application = subclient.applications.create(friendly_name=f"{company_id}_TWIML_APP")
            return application.sid
        return applications[0].sid

        




        
