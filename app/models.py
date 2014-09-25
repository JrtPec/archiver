from app import db

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64))
	facebook_id = db.Column(db.String(64))
	categories = db.relationship('Category', backref = 'user', lazy = 'dynamic', cascade="all, delete, delete-orphan")

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