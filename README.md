"# em-voip" 



#### .ENV
APP_TYPE = 'STAGE' #default

jwt_key = 'xxx@@@xxxxxxxxxxxx'



###### --- AWS S3

s3_access_key = xxxxx
s3_secret_key = xxxxx

s3_access_key_public = xxxxx
s3_secret_key_public = xxxxxx


###### ---- elasticsearch

ELASTIC_SEARCH_ARN = xxxxxx
ELASTIC_SEARCH_KIBANA = xxxxxxxxx
ELASTIC_SEARCH_CLOUD_ID = xxxxxxxxxx
ELASTIC_SEARCH_ENDPOINT = 'http://localhost:9200'  #local
ELASTIC_SEARCH_USERNAME = xxxxxxxx
ELASTIC_SEARCH_PASSWORD = xxxxx

###### --- mongo

MONGO_LOCAL = 'http://localhost:27071'
MONGO_DB_CLIENT = 'mongodb+srv:xxxxxxxx'


###### ---twilio
TWILIO_ACCOUNT_SID = xxxxxxxxx
TWILIO_AUTH_TOKEN = xxxxxxxxxx

TWILIO_MESSAGING_SERVICE_SID = xxxxxx
BASEURL_VOIP = xxxxxxx #link
TWILIO_TWIML_APP_SID = xxxx

###### - FLASK & CORS
ALLOWED_ORIGINS = xxxxxx
ALLOWED_ORIGINS_SOCKET= xxxxx
FLASK_PORT = xxxx

FLASK_DEBUG = xxxx


![EmVoip Web: index](https://github.com/iameo/em-voip/blob/main/voip/imgs/index.png)

![EmVoip Web: profile](https://github.com/iameo/em-voip/blob/main/voip/imgs/profile.png)


###### Checking Call Logic and logs: Busy, No Answer, Completed, and Failed
![Twilio Console](https://github.com/iameo/em-voip/blob/main/voip/imgs/twilio_console.png)