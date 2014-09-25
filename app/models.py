from app import db

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64))
	facebook_id = db.Column(db.String(64))

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def get_id(self):
		return unicode(self.id)

	def is_anonymous(self):
		return False