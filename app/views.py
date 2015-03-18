from app import app, lm, facebook, db
from flask.ext.login import current_user, login_required, login_user, logout_user
from flask import g, render_template, redirect, flash, session, url_for, request, abort, send_from_directory, send_file
from forms import *
from models import Settings
from datetime import datetime
from werkzeug import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, FILE_FOLDER
import os
import random

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path,'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

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

@app.route('/', methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
def index():
    settings = Settings.query.get(1)
    if settings is None:
        upper = 6
        lower = 1
    else:
        upper = settings.upper
        lower = settings.lower

    form = dobbel_form()

    if form.validate_on_submit():
        number = int(random.random()*(upper-(lower-1)) + lower)
    else:
        number = None

    return render_template(
		'index.html',
        form=form,
        number=number)

@app.route('/settings', methods = ['GET','POST'])
def settings():
    form = settings_form()
    settings = Settings.query.get(1)
    if settings is None:
        settings = Settings()

    if form.validate_on_submit():
        settings.lower = form.lower.data
        settings.upper = form.upper.data
        db.session.add(settings)
        db.session.commit()
    else:
        form.lower.data = settings.lower
        form.upper.data = settings.upper

    return render_template(
        'settings.html',
        form=form,
        title='instellingen')
