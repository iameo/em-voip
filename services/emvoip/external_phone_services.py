from pycountry import countries
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE


countries_code = {}

def isos_coverage(iso, code):
    """
    Fetch Country and the associated area code, given iso and code
    """
    country_name = ''
    country = ''

    _country = countries.get(alpha_2=iso)
    try:
        country_name = _country.name
    except:
        #in cases of empty iso data or no country name
        pass
    country = f"{country_name} (+{str(code)})" # NG (+234)
    countries_code.update({country:iso}) if len(country_name) > 1 else ""


def request_ext_countries():
    """
    Generate Countries and associated area code when user wants to get a number
    """
    
    for code, iso in COUNTRY_CODE_TO_REGION_CODE.items():
        if len(iso) > 1: #cases where there's multiple shared phone code. Example: GB, GG both share +44
            for val in iso:
                iso = ''.join(val)
                isos_coverage(iso, code)
        iso = ''.join(iso[0])
        isos_coverage(iso, code)
    countries_code_list = {x:y for y,x in countries_code.items()}
    return countries_code_list

