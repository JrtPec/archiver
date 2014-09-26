from app import db

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64))
	facebook_id = db.Column(db.String(64))
	categories = db.relationship('Category', backref = 'user', lazy = 'dynamic', cascade="all, delete, delete-orphan")
	entries = db.relationship('Entry', backref = 'user', lazy = 'dynamic', cascade="all, delete, delete-orphan")

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def get_id(self):
		return unicode(self.id)

	def is_anonymous(self):
		return False

class Category(db.Model):
	__tablename__ = 'category'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64))
	color = db.Column(db.String(64), default = "#F5F5F5")
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	entries = db.relationship('Entry', backref = 'category', lazy = 'dynamic')

class Entry(db.Model):
	__tablename__ = 'entry'
	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
	date = db.Column(db.DateTime)
	due_date = db.Column(db.DateTime)
	cents = db.Column(db.Integer)
	info = db.Column(db.String(140))
	check = db.Column(db.SmallInteger, default=0)

	def set_amount(self,euros):
		self.cents = int(euros*100)
		pass

	def get_amount(self):
		if self.cents == None:
			return None
		else:
			return float(self.cents)/100

	def is_checked(self):
		if self.check == 0:
			return False
		else:
			return True

	def toggle_check(self):
		if self.check == 0:
			self.check = 1
		else:
			self.check = 0
		pass

