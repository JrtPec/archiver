from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired as Required
from wtforms.validators import Length, optional,Regexp
from models import User, Category
from flask import g

class category_form(Form):
	name = TextField('name', validators=[Required(), Length(min=1,max=64)])
	color = TextField('color', validators=[optional(), Regexp(regex=r'^#[A-Fa-f0-9]{6}$',message='Please enter a hexadecimal color')])

	def __init__(self, name, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.unique_name = name

	def validate(self):
		if not Form.validate(self):
			return False
		if self.color.data == "":
			self.color.data = None
		if self.name.data != self.unique_name:
			category = Category.query.filter_by(name = self.name.data, user=g.user).first()
			if category != None:
				self.name.errors.append('You already have a category with this name.')
				return False
		return True

class delete_form(Form):
	pass