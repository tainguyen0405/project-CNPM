from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ==========================================
# USER
# ==========================================

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(
        db.String(150),
        nullable=False
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True
    )

    phone = db.Column(
        db.String(20)
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    address = db.Column(
        db.String(255)
    )

    role = db.Column(
        db.String(20),
        default="reader"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ==========================================
# LIBRARIAN STAFF
# ==========================================

class LibrarianStaff(db.Model):

    __tablename__ = "librarian_staff"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    employee_code = db.Column(
        db.String(50),
        unique=True
    )

    user = db.relationship(
        "User",
        backref="staff_profile"
    )


# ==========================================
# CATEGORY
# ==========================================

class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text
    )


# ==========================================
# BOOK
# ==========================================

class Book(db.Model):

    __tablename__ = "books"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    isbn = db.Column(
        db.String(30),
        unique=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    author = db.Column(
        db.String(150)
    )

    publisher = db.Column(
        db.String(150)
    )

    publish_year = db.Column(
        db.Integer
    )

    quantity = db.Column(
        db.Integer,
        default=1
    )

    available_copies = db.Column(
        db.Integer,
        default=1
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id")
    )

    category = db.relationship(
        "Category",
        backref="books"
    )
    def get_book_details(self):

        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "publisher": self.publisher
        }


# ==========================================
# BORROW RECORD
# ==========================================

class BorrowRecord(db.Model):

    __tablename__ = "borrow_records"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id")
    )

    borrow_date = db.Column(
        db.Date
    )

    due_date = db.Column(
        db.Date
    )

    return_date = db.Column(
        db.Date,
        nullable=True
    )

    status = db.Column(
        db.String(50),
        default="Borrowing"
    )

    fine_amount = db.Column(
        db.Float,
        default=0
    )

    user = db.relationship(
        "User",
        backref="borrows"
    )

    book = db.relationship(
        "Book",
        backref="borrows"
    )
    def calculate_fine(self):

        if self.return_date and self.return_date > self.due_date:

            days = (
                self.return_date -
                self.due_date
            ).days

            return days * 5000

        return 0


# ==========================================
# NOTIFICATION
# ==========================================

class Notification(db.Model):

    __tablename__ = "notifications"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    message = db.Column(
        db.String(255)
    )

    type = db.Column(
        db.String(50),
        default="info"
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship( 
        "User",
        backref="notifications"
    )
    def mark_as_read(self):

        self.is_read = True