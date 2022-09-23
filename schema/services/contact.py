from typing import Optional, Union
from pydantic import BaseModel, validator
import re
from services.middlewares.common import clean_payload


class ContactNumber(BaseModel):
    """
    ContactNumber is the base model for which other schema inherints from:

    args:
        is_shared: if the resource is shared (default: 0)
        is_primary: if the purchased phone number is primary contact (default: 0)
        area_code: the area code associated with the phone number (default: '')
    """
    is_shared: int
    is_primary: int
    area_code: str

    @validator("*", pre=True)
    def clean(cls, value):
        return clean_payload(value)


class ContactNumberPost(ContactNumber):
    """
    Schema for purchasing a phone number
    
    args necessary for allocating a number: area_code and country

    args:
        country: country where to purchase number from (default: United States)
    """
    country: str = 'US'


class ContactNumberPut(ContactNumberPost):
    """
    Schema post number buying (PUT request)
    
    forwarding_enabled: activate call forwarding on a number (default: 0)
    forward_to: if call forwarding is enabled, the contact call is forwarded to
    voice_greeting_enabled: activate voice mail greeting (default: 0)
    voice_greeting_url: (pre)-recorded messages will be converted to an url if voice greeting is enabled'
    label: phone number label

    """

    forwarding_enabled: int
    forward_to: Optional[str] = ''
    voice_greeting_enabled: int
    voice_greeting_url: Optional[str] = ''
    label: Optional[str]

    @validator('forward_to')
    def validate_forwarding(cls, v, values, **kwargs):
        forwarding_enabled = values.get('forwarding_enabled')

        phone_regex = re.compile("^(\+\d{1,3})?[-\s. ]*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$", re.IGNORECASE)
        contact_validity = phone_regex.match(v)
        if (forwarding_enabled == 1) and (v == '' and contact_validity is None):
            input_condition = 'Empty value' if not v else 'Input %s' % str(v)
            raise ValueError(f"Forwarding is enabled. {input_condition} is not a valid phone number.")
        return v


    @validator('voice_greeting_url')
    def validate_voice_greeting(cls, v, values, **kwargs):
        is_greeting = values.get('voice_greeting_enabled')
        if (is_greeting == 1) and v == '':
            raise ValueError("Voice Greeting is enabled. Kindly record your message so we can establish voicemail greeting.")
        return v

