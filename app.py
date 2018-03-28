#!/usr/local/bin/python

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import jsonify
from flask import url_for
from flask import flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import *
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
from functools import wraps
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Gamers NBA Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///gamersnba.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Facebook connect


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(
        open(
            'fb_client_secrets.json',
            'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Split the token on commas and select the
        first index that is, the key : value
        Then split token again on colons to pull out t
        he actual token value and replace the
        remaining quotes with empty string else the graph
        api would not decipher the value
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # Store token in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # See if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']

    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # Access token required to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # Verify if user exists else create a new user
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Decorator to ensure login
def login_required(f):
    @wraps(f)
    def x(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return x

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Franchise Information
@app.route('/franchise/JSON')
def franchiseJSON():
    franchises = session.query(Franchise).all()
    return jsonify(Franchises=[f.serialize for f in franchises])


@app.route('/franchise/<int:franchise_id>/roster/JSON')
def rosterJSON(franchise_id):
    franchise = session.query(Franchise).filter_by(id=franchise_id).one()
    roster = session.query(Player).filter_by(
        franchise_id=franchise_id).all()
    return jsonify(Roster=[r.serialize for r in roster])


@app.route('/franchise/<int:franchise_id>/roster/<int:player_id>/JSON')
def playerProfileJSON(franchise_id, player_id):
    Player_Profile = session.query(Player).filter_by(id=player_id).one()
    return jsonify(Player_Profile=Player_Profile.serialize)


# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Show all Franchises
@app.route('/franchise/')
def displayFranchises():
    franchises = session.query(Franchise).order_by(asc(Franchise.name))
    if 'username' not in login_session:
        return render_template('publicfranchises.html', franchises=franchises)
    else:
        return render_template('franchises.html', franchises=franchises)


# Create a new franchise
@app.route('/franchise/new/', methods=['GET', 'POST'])
@login_required
def newFranchise():
    if request.method == 'POST':
        newclub = Franchise(
            name=request.form['name'],
            image=request.form['image'],
            conference=request.form['conference'],
            user_id=login_session['user_id'])
        session.add(newclub)
        flash('%s Your New Basketball Franchise has been Successfully Negotiated. \
      Congratulations you are now a Franchise owner' % newclub.name)
        session.commit()
        return redirect(url_for('displayFranchises'))
    else:
        return render_template('newfranchise.html')


# Edit the details of a franchise
@app.route('/franchise/<int:franchise_id>/edit/', methods=['GET', 'POST'])
@login_required
def editFranchise(franchise_id):
    franchiseToRename = session.query(
        Franchise).filter_by(id=franchise_id).one_or_none()
    if franchiseToRename.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to \
    edit franchise. You must own a franchise to edit one.');}\
    </script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            franchiseToRename.name = request.form['name']
        if request.form['image']:
            franchiseToRename.image = request.form['image']
        if request.form['conference']:
            franchiseToRename.conference = request.form['conference']
        session.add(franchiseToRename)
        session.commit()
        flash(
            'Your Franchise has been Successfully renamed as %s' %
            franchiseToRename.name)
        return redirect(url_for('displayFranchises'))
    else:
        return render_template(
            'editfranchise.html',
            franchise=franchiseToRename)


# Delete a franchise
@app.route('/franchise/<int:franchise_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteFranchise(franchise_id):
    franchiseToDelete = session.query(
        Franchise).filter_by(id=franchise_id).one_or_none()
    if franchiseToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
    to delete this Franchise. You have to be a franchise owner \
    before you can delete!');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(franchiseToDelete)
        flash('%s no longer exists as a franchise' % franchiseToDelete.name)
        session.commit()
        return redirect(
            url_for(
                'displayFranchises',
                franchise_id=franchise_id))
    else:
        return render_template(
            'deletefranchise.html',
            franchise=franchiseToDelete)


# Show a franchise roster
@app.route('/franchise/<int:franchise_id>/')
@app.route('/franchise/<int:franchise_id>/roster/')
def displayRoster(franchise_id):
    franchise = session.query(Franchise).filter_by(
        id=franchise_id).one_or_none()
    creator = getUserInfo(franchise.user_id)
    roster = session.query(Player).filter_by(
        franchise_id=franchise_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicroster.html', roster=roster,
                               franchise=franchise, creator=creator)
    else:
        return render_template('roster.html', roster=roster,
                               franchise=franchise, creator=creator)


# Create a new player
@app.route(
    '/franchise/<int:franchise_id>/roster/new/',
    methods=[
        'GET',
        'POST'])
@login_required
def newPlayer(franchise_id):
    franchise = session.query(Franchise).filter_by(
        id=franchise_id).one_or_none()
    if login_session['user_id'] != franchise.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
    to add menu player to this franchise. You must be a franchise owner \
    to add players.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        newPlayer = Player(
            name=request.form['name'],
            age=request.form['age'],
            price=request.form['price'],
            position=request.form['position'],
            height=request.form['height'],
            weight=request.form['weight'],
            image=request.form['image'],
            ppg=request.form['ppg'],
            franchise_id=franchise_id,
            user_id=login_session['user_id'])
        session.add(newPlayer)
        session.commit()
        flash(
            '%s your new player has been Successfully Created' %
            (newPlayer.name))
        return redirect(
            url_for(
                'displayFranchises',
                franchise_id=franchise_id))
    else:
        return render_template('newplayer.html', franchise_id=franchise_id)


# Edit a Player Profile
@app.route(
    '/franchise/<int:franchise_id>/roster/<int:player_id>/edit',
    methods=[
        'GET',
        'POST'])
@login_required
def editPlayer(franchise_id, player_id):
    profileToEdit = session.query(Player).filter_by(id=player_id).one_or_none()
    franchise = session.query(Franchise).filter_by(
        id=franchise_id).one_or_none()
    if login_session['user_id'] != franchise.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
    to edit a player profile. You have to own a franchise to edit \
    the profile of a player!');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            profileToEdit.name = request.form['name']
        if request.form['age']:
            profileToEdit.age = request.form['age']
        if request.form['price']:
            profileToEdit.price = request.form['price']
        if request.form['height']:
            profileToEdit.height = request.form['height']
        if request.form['position']:
            profileToEdit.position = request.form['position']
        if request.form['weight']:
            profileToEdit.weight = request.form['weight']
        if request.form['image']:
            profileToEdit.image = request.form['image']
        if request.form['ppg']:
            profileToEdit.ppg = request.form['ppg']
        session.add(profileToEdit)
        session.commit()
        flash(
            'The Profile of %s was Successfully Edited' %
            (profileToEdit.name))
        return redirect(
            url_for(
                'displayFranchises',
                franchise_id=franchise_id))
    else:
        return render_template(
            'editplayerprofile.html',
            franchise=franchise,
            player=profileToEdit)


# Delete a player
@app.route(
    '/franchise/<int:franchise_id>/roster/<int:player_id>/delete',
    methods=[
        'GET',
        'POST'])
@login_required
def deletePlayerProfile(franchise_id, player_id):
    franchise = session.query(Franchise).filter_by(
        id=franchise_id).one_or_none()
    profileToDelete = session.query(
        Player).filter_by(id=player_id).one_or_none()
    if login_session['user_id'] != franchise.user_id:
        return "<script>function myFunction() {alert\
        ('You are not authorized to delete this player's profile. \
        You must be a franchise owner in order to delete \
        a player's profile.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(profileToDelete)
        session.commit()
        flash(
            '%s\'s Profile has been Successfully Deleted' %
            profileToDelete.name)
        return redirect(
            url_for(
                'displayFranchises',
                franchise_id=franchise_id))
    else:
        return render_template(
            'deleteplayerprofile.html',
            profile=profileToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('displayFranchises'))
    else:
        flash("You were not logged in")
        return redirect(url_for('displayFranchises'))


# Ensure the Global Variable __name__ is the entry to execute program
if __name__ == '__main__':
    app.secret_key = 'gamers_secret_hoops'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
