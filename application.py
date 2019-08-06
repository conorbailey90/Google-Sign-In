import json
import requests
import httplib2

from flask import (
    Flask,
    jsonify,
    session as login_session,
    redirect,
    url_for,
    request,
    make_response,
    render_template
)

from google.oauth2 import id_token
from google.auth.transport import requests



# Set up the application
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

def Is_Authenticated():
    return ('username' in login_session)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', name = login_session.get('username'), authenticated = Is_Authenticated())
    

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # (Receive token by HTTPS POST)
    # ...
    token = request.form['idtoken']
    print(token)
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
    except ValueError:
        # Invalid token
        pass
    
    login_session['username'] = idinfo['name']
    login_session['picture'] = idinfo['picture']
    login_session['email'] = idinfo['email']

    return redirect(url_for('index'))


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    username = login_session.get('username')
    if username != None:
        del login_session['username']
        del login_session['picture']
        del login_session['email']
    
    return redirect(url_for('index'))




if __name__ == "__main__":
    app.debug = True
    app.secret_key ='SUPER_SECRET_KEY'
    app.run(host='0.0.0.0', port=9000)