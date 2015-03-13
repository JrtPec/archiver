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

@app.route('/')
@app.route('/index')
def index():
	return render_template(
		'index.html')