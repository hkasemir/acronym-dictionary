import handlers
from flask import Flask, jsonify, request, url_for, abort, g, render_template
from flask import make_response, redirect
from flask import session as login_session

from flask_httpauth import HTTPBasicAuth
import json
import httplib2
import urllib
import requests
import random
import string

auth = HTTPBasicAuth()

CLIENT_ID = json.loads(open('secrets.json', 'r').read())['client_id']
CLIENT_SECRET = json.loads(open('secrets.json', 'r').read())['client_secret']
AUTH_URI = json.loads(open('secrets.json', 'r').read())['auth_uri']
TOKEN_URI = json.loads(open('secrets.json', 'r').read())['token_request_uri']
REDIRECT_URI = json.loads(open('secrets.json', 'r').read())['redirect_uri']

@auth.verify_password
def verify_token(token):
    user_id = User.verify_auth_token(token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        return False
    g.user = user
    return True

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/categories/add', methods=['POST', 'GET'])
def add_category():
    if request.method == 'POST':
        handlers.add_category(request.form)
        return redirect(url_for('main'))

    if request.method == 'GET':
        return render_template('category_create.html')

@app.route('/login')
def auth():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    params = {
            'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'state': state
            }

    return redirect(AUTH_URI + '?' + urllib.urlencode(params))

@app.route('/auth')
def login():
    #STEP 1 - Check state matches to ensure a third party
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.args.get('code')
    print "Step 1 - Complete, received auth code %s" % code

    #STEP 2 - Exchange for a token
    # Upgrade the authorization code into a credentials object
    step2_params = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'state': login_session['state']
            }
    headers = {'Accept': 'application/json'}
    credentials = requests.post(TOKEN_URI, headers=headers, json=step2_params)
    print(credentials.json()['access_token'])
          
    # Check that the access token is valid.
    access_token = credentials.json()['access_token']

    # # Verify that the access token is used for the intended user.
    # gplus_id = credentials.id_token['sub']
    # if result['user_id'] != gplus_id:
    #     response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
    #     response.headers['Content-Type'] = 'application/json'
    #     return response

    # # Verify that the access token is valid for this app.
    # if result['issued_to'] != CLIENT_ID:
    #     response = make_response(json.dumps("Token's client ID does not match app's."), 401)
    #     response.headers['Content-Type'] = 'application/json'
    #     return response

    # stored_credentials = login_session.get('credentials')
    # stored_gplus_id = login_session.get('gplus_id')
    # if stored_credentials is not None and gplus_id == stored_gplus_id:
    #     response = make_response(json.dumps('Current user is already connected.'), 200)
    #     response.headers['Content-Type'] = 'application/json'
    #     return response
    print "Step 2 Complete! Access Token : %s " % access_token
    url = 'https://api.github.com/user?access_token=%s' % access_token

    #STEP 3 - Find User or make a new one
    
    #Get user info
    answer = requests.get(url)
  
    data = answer.json()
    print data

    username = data['login']
    #see if user exists, if it doesn't make a new one
    user = handlers.get_or_create_user(username, access_token)
    #STEP 4 - Make token
    cookie = user.generate_auth_cookie()
    login_session['cookie'] = cookie

    #STEP 5 - Send back token to the client 
    return jsonify({'token': cookie.decode('ascii')})

@app.route('/token')
# @auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})
# 
# @app.route('/api/resource')
# @auth.login_required
# def get_resource():
#     return jsonify({ 'data': 'Hello, %s!' % g.user.username })



if __name__ == '__main__':
    app.debug = True
    app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=5000)

