from voip import create_app
from flask import render_template
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Origin, Accept, Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,LINK,UNLINK,COPY,LOCK,UNLOCK,PATCH')
  return response




#fallback route for voice
@app.route('/voip/voice/fallback')
def get():
    from twilio.twiml.voice_response import VoiceResponse
    from flask import Response
    resp = VoiceResponse()
    resp.say("Voice Connection is currently under maintenance. Please try again in a few minutes.")
    resp.hangup()
    return Response(str(resp), mimetype='text/xml')


@app.route('/voip/home', endpoint='home')
def voip_home():
  return render_template('index.html')

@app.route('/login')
def loginn():
  return render_template('login.html')


if __name__ == '__main__':
    # socketio.run(app, debug=True)
    app.run(port=os.getenv('FLASK_PORT'), debug=os.getenv('FLASK_DEBUG'))