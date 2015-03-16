from flask.ext.wtf import Form
from wtforms import IntegerField
from wtforms.validators import DataRequired as Required
from wtforms.validators import Length, optional,Regexp,NumberRange
from flask import g

class settings_form(Form):
	lower = IntegerField('lower',validators=[Required()])
	upper = IntegerField('upper',validators=[Required()])

class dobbel_form(Form):
	pass