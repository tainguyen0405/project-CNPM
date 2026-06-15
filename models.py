from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role     = db.Column(db.String(20), default='reader')
    # role: admin / librarian / reader

class Book(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    title    = db.Column(db.String(200), nullable=False)
    author   = db.Column(db.String(100))
    category = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)

class BorrowRecord(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id     = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrow_date = db.Column(db.Date)
    due_date    = db.Column(db.Date)
    return_date = db.Column(db.Date, nullable=True)

    user = db.relationship('User', backref='borrows')
    book = db.relationship('Book', backref='borrows')