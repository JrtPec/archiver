from app import app, lm, facebook, db
from flask.ext.login import current_user, login_required, login_user, logout_user
from flask import g, render_template, redirect, flash, session, url_for, request, abort, send_from_directory, send_file
from models import User, Category, Entry, File
from forms import category_form, delete_form, entry_form
from datetime import datetime
from werkzeug import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, FILE_FOLDER
import os

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path,'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.before_request
def before_request():
	g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(id)

@app.errorhandler(404)
def internal_error(error):
    flash('That page was not found, sorry!')
    return redirect(url_for('index'))

@app.errorhandler(401)
def internal_error(error):
    flash("You don't have that permission, sorry!")
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('Something went wrong, sorry!')
    return redirect(url_for('index'))

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
            abort(404)
        name = category.name
    else:
        name = None
    form = category_form(name)

    if form.validate_on_submit():
        if action == "new":
            category = Category(
                name=form.name.data, 
                color=form.color.data, 
                user=g.user)
        elif action == "edit":
            category.name = form.name.data
            category.color = form.color.data
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('settings'))

    elif request.method != 'POST':
        if action=="edit":
            form.name.data = category.name
            form.color.data = category.color
    return render_template(
        'category.html',
        title = "Configure category",
        form = form)

@app.route('/new_entry', methods = ['GET','POST'])
@app.route('/new_entry/<file_id>', methods = ['GET','POST'])
@login_required
def new_entry(file_id=None):
    if g.user.categories.first() == None:
        flash('You need at least one category to start adding entries')
        return redirect(url_for('category',action='new'))

    form = entry_form()
    form.category.choices = [(c.id, c.name) for c in g.user.categories]

    if form.validate_on_submit():
        entry = Entry(user=g.user,
            category_id=form.category.data,
            date=form.date.data,
            due_date=form.due_date.data,
            info=form.info.data)
        if form.amount.data:
            entry.set_amount(euros=form.amount.data)
        if form.check.data == True:
            entry.check = 1

        if file_id:
            file = File.query.get(file_id)
            if file == None:
                abort(500)
            elif file.user != g.user:
                abort(401)
            else:
                file.entry = entry
                db.session.add(file)
        db.session.add(entry)
        db.session.commit()
        flash('New entry added!')
        return redirect(url_for('index'))
    elif request.method != 'POST':
        form.date.data = datetime.utcnow()
    return render_template(
        'entry.html',
        title = 'New entry',
        form = form)

@app.route('/edit_entry', methods = ['GET','POST'])
@login_required
def edit_entry(id):
    entry = Entry.query.get(id)
    if entry == None:
        abort(404)
    elif entry.user != g.user:
        abort(401)

    form = entry_form()
    form.category.choices = [(c.id, c.name) for c in g.user.categories]

    if form.validate_on_submit():
        entry.category_id = form.category.data
        entry.date = form.date.data
        entry.due_date = form.due_date.data
        entry.info = form.info.data
        if form.amount.data == None:
            entry.cents == None
        else:
            entry.set_amount(euros=form.amount.data)
        if form.check.data == True:
            entry.check = 1
        else:
            entry.check = 0
        db.session.add(entry)
        db.session.commit()
        flash('Entry eddited!')
        return redirect(url_for('entries'))
    elif request.method != 'POST':
        form.category.choices.insert(0,(entry.category.id,entry.category.name))
        form.date.data = entry.date
        form.due_date.data = entry.due_date
        form.info.data = entry.info
        form.amount.data = entry.get_amount()
        form.check.data = entry.is_checked()
    return render_template(
        'entry.html',
        title = 'Configure entry',
        form = form)

@app.route('/check_entry/<id>')
@login_required
def check_entry(id):
    entry = Entry.query.get(id)
    if entry == None:
        abort(404)
    elif entry.user != g.user:
        abort(401)

    entry.toggle_check()
    db.session.add(entry)
    db.session.commit()
    flash('Check!')
    return redirect(url_for('entries'))        

@app.route('/entries')
@login_required
def entries():
    entries = g.user.entries.order_by(Entry.date.desc())
    return render_template(
        'entries.html',
        title = 'Entries',
        entries=entries)

@app.route('/delete/<type>/<id>', methods = ['GET','POST'])
@login_required
def delete(type,id):
    form = delete_form()
    if form.validate_on_submit():
        if type == "category":
            c = Category.query.get(id)
            redir = 'settings'
        elif type == "entry":
            c = Entry.query.get(id)
            redir = 'entries'
        elif type == 'file':
            c = File.query.get(id)
            redir = 'entries'
        else:
            c = None
        if c != None:
            db.session.delete(c)
            db.session.commit()
            flash('Delete successful')
            return redirect(url_for(redir))
        else:
            abort(500)
    return render_template(
        'delete.html',
        title = 'Delete',
        form = form,
        thing = type)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def get_extension(filename):
    return filename.rsplit('.',1)[1].lower()

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(str(g.user.facebook_id)+"_"+str(datetime.utcnow().isoformat().replace(".","-"))+"."+get_extension(file.filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            file_db = File(user=g.user,filename=filename)
            db.session.add(file_db)
            db.session.commit()
            flash('Upload successful')
            return redirect(url_for('new_entry',file_id=file_db.id))
        else:
            flash('File not allowed')
            abort(500)
    else:
        abort(500)

@app.route('/file/<id>')
@login_required
def file(id):
    file = File.query.get(id)
    if file == None:
        abort(404)
    elif file.user != g.user:
        abort(401)
    else:
        return send_from_directory(os.path.join(app.root_path,FILE_FOLDER),file.filename)
