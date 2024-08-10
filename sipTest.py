from flask import Flask, Response, request, jsonify, render_template
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
api_key = os.getenv('TWILIO_API_KEY')
api_secret = os.getenv('TWILIO_API_SECRET')
twiml_app_sid = os.getenv('TWIML_APP_SID')
twilio_number = os.getenv('TWILIO_NUMBER')

# Ensure all required environment variables are set
required_env_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_API_KEY', 'TWILIO_API_SECRET', 'TWIML_APP_SID', 'TWILIO_NUMBER']
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")
    
@app.route('/')
def index():
    return render_template('index.html', twilio_number=twilio_number)

@app.route('/token')
def get_token():
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    api_key = os.environ['TWILIO_API_KEY']
    api_secret = os.environ['TWILIO_API_SECRET']
    twiml_application_sid = os.environ['TWIML_APP_SID']

    token = AccessToken(account_sid, api_key, api_secret, identity='user')

    voice_grant = VoiceGrant(
        outgoing_application_sid=twiml_application_sid,
        incoming_allow=True,
    )
    token.add_grant(voice_grant)

    jwt_token = token.to_jwt()
    return jsonify(token=jwt_token)

@app.route('/make-call', methods=['POST'])
def make_call():
    app.logger.info('Received request to /make-call')
    app.logger.info(f'Request data: {request.json}')
    
    to_number = request.json.get('To')
    from_number = request.json.get('From')
    
    app.logger.info(f'Attempting to call {to_number} from {from_number}')
    
    response = VoiceResponse()
    dial = response.dial(caller_id=from_number)
    dial.number(to_number)
    
    twiml = str(response)
    app.logger.info(f'Generated TwiML: {twiml}')
    
    return Response(twiml, mimetype='text/xml')


if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
