from db import db_fetch

from utils.twilio_supported_langs import available_langs




def _validate_phone(contact, country=None):
    """
    this function validates a provided number and parses it with the given country

    if provided number is parsed as a phone number, next step is ensuring it is valid

    if True:
        return phone number in E184 format (ex: +234801111222)
    Else:
        return False

    Args:
        contact: phone number in any format
        country: country where phone number is purchased: fallback is None (which falls back to US)

    """
    contact_, contact_valid_ = phone_number_parser(contact, country)
    return contact_, contact_valid_



def phone_number_parser(contact, country=None):
    """parses a typical phone number, checking its validity"""
    
    import phonenumbers
    from phonenumbers.phonenumberutil import NumberParseException

    if country is None:
        country = 'NG'

    try:
        contact = phonenumbers.parse(contact, country)
    except NumberParseException:
        return str(contact), False
    valid_num = phonenumbers.is_valid_number(contact)
    if valid_num:
        return f"+{contact.country_code}{contact.national_number}", True 
    else:
        return str(contact), False



def get_account(index="subaccounts", *, lookup=None):
    key, value = lookup.popitem()
    query = {
            "query": {
            "bool": {
                "must": [
                {
                    "match_phrase": {
                        f"{key}": f"{value}"
                    }
                },
                {
                    "match_phrase": {
                        "is_delete": 0
                    }
                }
                
                ]
            }
            }
        }  
    try:
        account = db_fetch(index=index, query=query)
    except IndexError:
        return None
    return account



def country_fetcher(account_id):
    """
    convert country name to its alpha_2 identifier: NIGERIA => NG
    """
    import pycountry

    alpha_2 = None

    try:
        country = get_account("accounts", lookup={"account_id":account_id})['country'] or 'Nigeria'
        try:
            alpha_2 = pycountry.countries.get(name=country).alpha_2
        except (AttributeError, LookupError):
            return alpha_2
    except:
        return alpha_2
        


def fetch_caller_lang(caller_country):
    language = next((key for key in available_langs if key.endswith(str(caller_country))), None)
    language = 'en-US' if language is None else language
    return language



