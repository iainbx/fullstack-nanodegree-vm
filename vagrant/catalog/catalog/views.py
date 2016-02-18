# Catalog App Views
from catalog import app, db_session
from catalog.models import Category, Item, User
from catalog.forms import CategoryForm, ItemForm

from flask import render_template, request, redirect, url_for, jsonify, flash
from flask import session, abort, send_from_directory, make_response
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from werkzeug import secure_filename
from flask_wtf.file import FileField
from datetime import datetime
import os

# Show catalog
@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = db_session.query(Category).all()
    return render_template('catalog.html',categories=categories)


# Show category
@app.route('/category/<name>/')
@app.route('/category/<name>/items')
def category(name):
    category = db_session.query(Category).filter_by(name = name).one()
    
    if category is None:
        abort(404)
    
    #items = db_session.query(Item).filter_by(category_id = category.id)
    return render_template('category.html', category=category, items=category.items)


# New category    
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'user_id' not in session:
        return redirect('/login')
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, user_id = session['user_id'])
        db_session.add(category)
        db_session.commit()
        flash("New category created.")
        return redirect(url_for('catalog'))
    return render_template('newCategory.html', form=form)
   

# Edit category
@app.route('/category/<name>/edit/', methods = ['GET', 'POST'])
def editCategory(name):
    if 'user_id' not in session:
        return redirect('/login')
    
    category = db_session.query(Category).filter_by(name = name).one()
    
    if category is None:
        abort(404)
    
    if category.user_id != session['user_id']:
        abort(401)
      
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        form.populate_obj(category)
        db_session.add(category)
        db_session.commit()
        flash("Category %s edited." % category.name)
        return redirect(url_for('category', name=category.name))
    return render_template('editCategory.html', category=category, form=form)


# Delete category
@app.route('/category/<name>/delete/', methods = ['GET','POST'])
def deleteCategory(name):
    if 'user_id' not in session:
        return redirect('/login')
    
    category = db_session.query(Category).filter_by(name = name).one()
    
    if category is None:
        abort(404)
    
    if category.user_id != session['user_id']:
        abort(401)
    
    if request.method == 'POST':
        # delete the category, and related items should be deleted automatically
        db_session.delete(category)
        db_session.commit()
        flash('%s Successfully Deleted' % category.name)
        return redirect(url_for('catalog'))
    else:
        return render_template('deleteCategory.html',category=category)


# Show item
@app.route('/item/<name>')
def item(name):
    item = db_session.query(Item).filter_by(name=name).one()
    
    if item is None:
        abort(404)
    
    return render_template('item.html', item=item)

# Item image 
@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# New item    
#TODO: route that includes category
@app.route('/item/new/', methods=['GET', 'POST'])
def newItem():
    if 'user_id' not in session:
        return redirect('/login')
    form = ItemForm()
    categories = db_session.query(Category.id, Category.name).all()
    form.category.choices = categories
    if form.validate_on_submit():
        filename = None
        # check if user uploaded file and sanitize filename
        if form.image.has_file():
            # gets the filename?
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # create new item and commit to database
        item = Item(
            name=form.name.data,
            description=form.description.data,
            category_id=form.category.data,
            image=filename,
            user_id=session['user_id'],
            pub_date = datetime.utcnow()
            )
        db_session.add(item)
        db_session.commit()
        flash("New item created.")
        return redirect(url_for('item', name=item.name))
    return render_template('newItem.html', form=form)
   

# Edit item
@app.route('/item/<name>/edit/', methods = ['GET', 'POST'])
def editItem(name):
    if 'user_id' not in session:
        return redirect('/login')
    
    item = db_session.query(Item).filter_by(name = name).one()
    
    if item is None:
        abort(404)
    
    if item.user_id != session['user_id']:
        abort(401)
      
    form = ItemForm(obj=item)
    categories = db_session.query(Category.id, Category.name).all()
    form.category.choices = categories
    if form.validate_on_submit():
        #form.populate_obj(item)
        item.name=form.name.data
        item.description=form.description.data
        item.category_id=form.category.data

        filename = None
        # check if user uploaded file and sanitize filename
        if form.image.has_file():
            # gets the filename?
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image=filename
        db_session.add(item)
        db_session.commit()
        flash("Item %s edited." % item.name)
        return redirect(url_for('item', name=item.name))
    return render_template('editItem.html', item=item, form=form)


# Delete item
@app.route('/item/<name>/delete/', methods = ['GET','POST'])
def deleteItem(name):
    if 'user_id' not in session:
        return redirect('/login')
    
    item = db_session.query(Item).filter_by(name = name).one()
    
    if item is None:
        abort(404)
    
    if item.user_id != session['user_id']:
        abort(401)
      
    if request.method == 'POST':
        db_session.delete(item)
        db_session.commit()
        flash('%s Successfully Deleted' % item.name)
        return redirect(url_for('catalog'))
    else:
        return render_template('deleteItem.html', item = item)

#################### AUTHENTICATION #######################

# login
@app.route('/login')
def login():
    # create a state token to prevent request forgery
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
            for x in range(32))
    session['state'] = state
    return render_template('login.html', STATE=state)

# logout
@app.route('/logout')
def logout():
    if 'provider' in session:
        if session['provider'] == 'google':
            gdisconnect()
            del session['gplus_id']
            del session['access_token']
        if session['provider'] == 'facebook':
            fbdisconnect()
            del session['facebook_id']
        del session['username']
        del session['email']
        del session['picture']
        del session['user_id']
        del session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('catalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('catalog'))

# User Helper Functions


def createUser(session):
    newUser = User(name=session['username'], email=session[
                   'email'], picture=session['picture'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/clearsession')
def clearSession():
    login_session.clear()
    flash("session cleared.")
    return redirect(url_for('catalog'))


# google    
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('google_client_secrets.json', scope='')
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

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    CLIENT_ID = json.loads(
        open('google_client_secrets.json', 'r').read())['web']['client_id']
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']
    session['provider'] = 'google'
    
    # create user if new
    user_id = getUserID(session['email']) 
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    #access_token = login_session['access_token']
    #print 'In gdisconnect access token is %s', access_token
    #print 'User name is: ' 
    #print login_session['username']
    if 'access_token' not in session:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] != '200':
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

# facebook authorization
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.5/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.5/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    session['provider'] = 'facebook'
    session['username'] = data["name"]
    session['email'] = data["email"]
    session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.5/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(session['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += session['username']

    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = session['facebook_id']
    # The access token must me included to successfully logout
    access_token = session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

