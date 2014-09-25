from app import app, lm, facebook, db
from flask.ext.login import current_user, login_required, login_user, logout_user
from flask import g, render_template, redirect, flash, session, url_for, request, abort
from models import User, Category
from forms import category_form, delete_form

@app.before_request
def before_request():
	g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(id)

@app.errorhandler(404)
def internal_error(error):
    flash('That page was not found, sorry!')
    return redirect(url_for('/'))

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('Something went wrong, sorry!')
    return redirect(url_for('/'))

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

@app.route('/settings')
@login_required
def settings():
    return render_template(
        'settings.html',
        title = "Settings")

@app.route('/category/<action>/<id>', methods = ['GET','POST'])
@app.route('/category/<action>', methods = ['GET','POST'])
@login_required
def category(action, id=None):
    if action=="edit":
        category = Category.query.get(id)
        if category == None:
            return redirect(url_for('settings'))
        name = category.name
    else:
        name = None
    form = category_form(name)

    if form.validate_on_submit():
        if action == "new":
            category = Category(name=form.name.data, color=form.color.data, user=g.user)
        elif action == "edit":
            category.name = form.name.data
            category.color = form.color.data
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('settings'))

    elif request.method != 'POST':
        if category:
            form.name.data = category.name
            form.color.data = category.color
    return render_template(
        'category.html',
        title = "Configure category",
        form = form)

@app.route('/delete/<type>/<id>', methods = ['GET','POST'])
@login_required
def delete(type,id):
    form = delete_form()
    if form.validate_on_submit():
        if type == "category":
            c = Category.query.get(id)
            if category != None:
                db.session.delete(c)
                db.session.commit()
                flash('Category deleted')
            return redirect(url_for('settings'))
        else:
            abort(500)
    return render_template(
        'delete.html',
        title = 'Delete',
        form = form,
        thing = type)
