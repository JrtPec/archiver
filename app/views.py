from app import app
from flask.ext.login import current_user
from flask import g, render_template

@app.before_request
def before_request():
	g.user = current_user

@app.route('/')
@app.route('/index')
def index():
	return render_template(
		'index.html')