from app import app, lm, facebook, db
from flask.ext.login import current_user, login_required, login_user, logout_user
from flask import g, render_template, redirect, flash, session, url_for, request
from models import User

@app.before_request
def before_request():
	g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(id)

@app.route('/login')
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index'))
	return render_template(
    	'login.html', 
        title = 'Log In')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

@app.route("/facebook_login")
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next'), _external=True))

@app.route("/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None or 'access_token' not in resp:
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))

    session['facebook_token'] = (resp['access_token'], '')

    data = facebook.get('/me').data
    if 'id' in data and 'name' in data:
        user_id = data['id']
        user_name = data['name']
    if 'email' in data:
        user_email = data['email']

    user = User.query.filter_by(facebook_id = user_id).first()

    if user is None:
        name = user_name
        user = User(name = name, facebook_id = user_id)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/')
@app.route('/index')
@login_required
def index():
	return render_template(
		'index.html')