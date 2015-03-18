from app import db

class Settings(db.Model):
	__tablename__ = 'settings'
	id = db.Column(db.Integer, primary_key = True)
	upper = db.Column(db.Integer, default=6)
	lower = db.Column(db.Integer, default=1)