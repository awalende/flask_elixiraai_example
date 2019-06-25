import flask
import logging
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc.user_session import UserSession
from flask import Flask, jsonify


app = Flask(__name__)


# Our OIDC Provider
ISSUER = 'https://login.elixir-czech.org/oidc/'

# This is portal-dev oidc client
CLIENT = 'b649ab06-8633-4aaa-943e-fe97882c0039'


# Enter the client secret for portal-dev client here!
CLIENT_SECRET = 'CLIENT SECRET HERE'

# Random name
PROVIDER_NAME = 'provider1'

# We configurate our provider with the fields from above
PROVIDER_CONFIG = ProviderConfiguration(issuer=ISSUER, client_metadata=ClientMetadata(CLIENT, CLIENT_SECRET))


# Make sure, that this server name (portal-dev.denbi.de) is 127.0.0.1 in your /etc/localhost
# If you want to start this on standard port 80, you'll have to run this flask app as root.
app.config.update({'SERVER_NAME': 'portal-dev.denbi.de',
                   'SECRET_KEY': 'dev_kefgdsgfdfsgy', # CHANGE THIS
                   'SESSION_PERMANENT': True, # turn on flask session support
                   'PERMANENT_SESSION_LIFETIME': 2592000, # session time in seconds (30 days)
                    'DEBUG': True})


# Create auth object with our defined provider and link it with flask app
auth = OIDCAuthentication({PROVIDER_NAME : PROVIDER_CONFIG}, app)

# When simply pointing the browser to http://portal-dev.denbi.de, directly return token contents on screen.
# Route to ELIXIR AAI and authenticate if user is not logged in.
@app.route('/')
@auth.oidc_auth(PROVIDER_NAME)
def login1():
    user_session = UserSession(flask.session)
    return jsonify(access_token=user_session.access_token, id_token=user_session.id_token, userinfo=user_session.userinfo)

# Redirect to elixir log-out page
@app.route('/logout')
@auth.oidc_logout
def logout():
    return "You've been successfully logged out!"

# If something is messed up
@auth.error_view
def error(error=None, error_description=None):
    return jsonify({'error': error, 'message': error_description})

# Be careful when running in production, use Apache with HAProxy and SSL in front.
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    auth.init_app(app)
    app.run()

