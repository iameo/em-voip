from typing import Optional, Union
from pydantic import BaseModel, validator
import re



class ContactNumber(BaseModel):
    is_shared: int
    is_primary: int
    area_code: str


class ContactNumberPost(ContactNumber):
    country: str


class ContactNumberPut(ContactNumberPost):
    forwarding_enabled: int
    forward_to: Optional[str]
    voice_greeting_enabled: int
    voice_greeting_url: Optional[str]
    label: Optional[str]

    @validator('forward_to')
    def validate_xxx(cls, v, values, **kwargs):
        forwarding_enabled = values.get('forwarding_enabled')
        phone_regex = re.compile("^(\+\d{1,3})?[-\s. ]*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$", re.IGNORECASE)
        contact_validity = phone_regex.match(v)
        if forwarding_enabled and (v == '' or contact_validity is None):
            input_condition = 'Empty value' if not v else 'Input %s' % str(v)
            raise ValueError(f"Forwarding is enabled. {input_condition} is not a valid phone number.")
        return v


    @validator('voice_greeting_url')
    def validate_voice_greeting(cls, v, values, **kwargs):
        is_greeting = values.get('voice_greeting_enabled')
        if is_greeting and v == '':
            raise ValueError("Voice Greeting is enabled. Kindly record your message.")
        return v

