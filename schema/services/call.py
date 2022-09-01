from typing import List, Optional
from pydantic import BaseModel


class CallBase(BaseModel):
    """
    CallBase is a base model that holds vital information for a call

    direction: (inbound|outbound)
    to: recipent of the call
    ____
    from_: caller
    call_status: status of the call (in-progress, failed, busy, completed, etc)
    """
    direction: str
    to: str


class CallPost(CallBase):
    """
    CallPost

    Schema for POST request at any time to your call index/table
    """
    from_: str
    call_status: str


class CallLogPost(CallBase):
    call_note: str
    author: str


class CallLogPut(CallLogPost):
    pass


#Feedback on Call

class FeedBackBase(BaseModel):
    """
    Feedback can be utilized after call ends, to facilitate call experience

    args:
        quality score: integer to depict the quality of the call (1-5). 5 decribes a perfect score.
        issue: if there's an issue (or more). List includes imperfect-audio, \
                dropped-call, incorrect-caller-id, post-dial-delay, digits-not-captured, \
                audio-latency, unsolicited-call, or one-way-audio
        message: string that holds optional information of the call
    """
    quality_score: int
    issues: List[str]
    message: Optional[str]

class FeedBackPost(FeedBackBase):
    call_sid: str

class FeedBackPut(FeedBackBase):
    pass



#Lead
class LeadIdentity(BaseModel):
    """"
    Schema for identifying lead on call in progress mode
    """
    contact: str
    lead_id: str


##### arbitary loading
call_post = CallPost()
call_log_post = CallLogPost()
call_log_put = CallLogPut()
feedback_post = FeedBackPost()
feedback_put = FeedBackPut()
lead_identity = LeadIdentity()