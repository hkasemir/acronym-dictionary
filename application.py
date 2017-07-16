import handlers
from flask import Flask, flash, url_for, render_template
from flask import make_response, redirect, request
from flask import session as login_session

import json
import urllib
import requests
import random
import string

CLIENT_ID = json.loads(open('secrets.json', 'r').read())['client_id']
CLIENT_SECRET = json.loads(open('secrets.json', 'r').read())['client_secret']
AUTH_URI = json.loads(open('secrets.json', 'r').read())['auth_uri']
TOKEN_URI = json.loads(open('secrets.json', 'r').read())['token_uri']
REDIRECT_URI = json.loads(open('secrets.json', 'r').read())['redirect_uri']
APP_SECRET_KEY = json.loads(open('secrets.json', 'r').read())['app_secret_key']

app = Flask(__name__)


def getUsername():
    if 'username' in login_session:
        return login_session['username']
    return None


def verify_session():
    # by making use of flask's login_session, we just check to see if the user
    # has been encoded in the login_session. If so, they have authenticated
    # and provided their github username to our users table
    if getUsername():
        return True
    else:
        return False


@app.route('/')
def main():
    return handlers.show_main()


@app.route('/definitions/json')
def words_json():
    return handlers.get_words_json()


@app.route('/definitions/<word>/json')
def single_word_json(word):
    return handlers.get_single_word_json(word)


@app.route('/categories/json')
def categories_json():
    return handlers.get_categories_json()


@app.route('/categories', methods=['POST', 'GET'])
def add_category():
    if request.method == 'POST':
        handlers.add_category(request.form)
        return redirect(url_for('main'))

    if request.method == 'GET':
        return handlers.show_add_category()


@app.route('/categories/<categoryname>')
def show_category(categoryname):
    return handlers.show_category(categoryname)


@app.route('/categories/<categoryname>/delete', methods=['POST', 'GET'])
def delete_category(categoryname):
    if request.method == 'POST':
        if handlers.category_has_words(categoryname):
            flash('Can\'t delete a category with words in it', 'error')
            return redirect(
                    url_for('show_category', categoryname=categoryname))
        handlers.delete_category(categoryname)
        return redirect(url_for('main'))

    if request.method == 'GET':
        if handlers.category_has_words(categoryname):
            flash('Can\'t delete a category with words in it', 'error')
            return redirect(
                    url_for('show_category', categoryname=categoryname))
        return handlers.show_delete_category(categoryname)


@app.route('/definitions', methods=['POST', 'GET'])
def add_definition():
    if not verify_session():
        login_session['return_url'] = url_for('add_definition')
        return redirect('/login')
    if request.method == 'POST':
        definition = handlers.add_word(request.form)
        return redirect(url_for('show_definition', word=definition.word))

    if request.method == 'GET':
        return handlers.show_add_word()


@app.route('/definitions/<word>')
def show_definition(word):
    return handlers.show_word(word)


@app.route('/definitions/<word>/edit', methods=['POST', 'GET'])
def edit_definition(word):
    if not verify_session():
        login_session['return_url'] = url_for('edit_definition', word=word)
        return redirect('/login')
    if request.method == 'POST':
        if handlers.user_created_word(word):
            updated = handlers.edit_word(word, request.form)
            return redirect(url_for('show_definition', word=updated.word))
        flash('Can\'t edit a word you did not create', 'error')
        return redirect(url_for('show_definition', word=word))

    if request.method == 'GET':
        if handlers.user_created_word(word):
            return handlers.show_edit_word(word)
        flash('Can\'t edit a word you did not create', 'error')
        return redirect(url_for('show_definition', word=word))


@app.route('/definitions/<word>/delete', methods=['POST', 'GET'])
def delete_definition(word):
    if not verify_session():
        login_session['return_url'] = url_for('delete_definition', word=word)
        return redirect('/login')
    if request.method == 'POST':
        if handlers.user_created_word(word):
            categoryname = handlers.delete_word(word)
            return redirect(
                    url_for('show_category', categoryname=categoryname))
        flash('Can\'t delete a word you did not create', 'error')
        return redirect(url_for('show_definition', word=word))

    if request.method == 'GET':
        if handlers.user_created_word(word):
            return handlers.show_delete_word(word)
        flash('Can\'t delete a word you did not create', 'error')
        return redirect(url_for('show_definition', word=word))


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    params = {
            'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'state': state
            }

    return redirect(AUTH_URI + '?' + urllib.urlencode(params))


@app.route('/logout')
def logout():
    login_session.pop('username', None)
    login_session.pop('return_url', None)
    login_session.pop('avatar_url', None)
    login_session.pop('state', None)
    return redirect(url_for('main'))


@app.route('/auth')
def auth():
    # STEP 1 - Check state matches to ensure a third party
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # STEP 2 - Exchange for a token
    # Upgrade the authorization code into an authentication token
    code = request.args.get('code')
    step2_params = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'state': login_session['state']
            }
    headers = {'Accept': 'application/json'}
    credentials = requests.post(TOKEN_URI, headers=headers, json=step2_params)
    access_token = credentials.json()['access_token']

    # STEP 3 - Find User or make a new one
    # Get user info
    url = 'https://api.github.com/user?access_token=%s' % access_token
    user = requests.get(url)
    data = user.json()
    username = data['login']
    # see if user exists, if it doesn't make a new one
    user = handlers.get_or_create_user(username, access_token)

    # STEP 4 - set login_session creds and redirect
    login_session['username'] = user.username
    login_session['avatar_url'] = data['avatar_url']
    redirect_url = '/'
    if 'return_url' in login_session:
        # they were redirected to login while trying to access a specific page
        # so send them back there
        redirect_url = login_session['return_url']
    response = make_response(redirect(redirect_url))
    return response


if __name__ == '__main__':
    app.debug = True
    app.secret_key = APP_SECRET_KEY
    app.run(host='0.0.0.0', port=5000)
