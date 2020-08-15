from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
	__tablename__ = 'User'
	id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	name = db.Column(db.String(1000))
	sheets = db.relationship('Sheet', backref='User', lazy=True)

class Sheet(db.Model):
	__tablename__ = 'Sheet'
	id = db.Column(db.Integer, primary_key=True)
	sheet_name = db.Column(db.String(1000))
	sheet_title_col = db.Column(db.Integer, nullable=False)
	sheet_link_col = db.Column(db.Integer, nullable=False)
	starting_row = db.Column(db.Integer, nullable=False)
	sheet_id = db.Column(db.String(10000), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)



