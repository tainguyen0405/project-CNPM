from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()
# =================================================
# USER
# # =================================================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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
        db.String(30),
        default="reader"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# -----------------------------
# Update Profile
# -----------------------------
    def update_profile(
        self,
        full_name,
        email,
        phone,
        address
    ):
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.address = address
# -----------------------------
# Change Password
# -----------------------------
    def change_password(
        self,
        new_password
    ):
        self.password = new_password
# -----------------------------
# User Information
# -----------------------------
    def get_user_info(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "role": self.role,
            "created_at": self.created_at
        }
# =================================================
# LIBRARIAN STAFF
# =================================================

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
        backref=db.backref(
            "staff_profile",
            uselist=False
        )
    )

# =================================================
# CATEGORY
# =================================================

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

    def get_category_details(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

# =================================================
# BOOK
# =================================================

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

    # -----------------------------
    # Book Details
    # -----------------------------
    def get_book_details(self):
        return {
            "id": self.id,
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "publisher": self.publisher,
            "publish_year": self.publish_year,
            "quantity": self.quantity,
            "available_copies": self.available_copies,
            "category":
                self.category.name
                if self.category
                else None,
            "created_at": self.created_at
        }


# =================================================
# BORROW RECORD
# =================================================

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
        backref="borrow_records"
    )

    book = db.relationship(
        "Book",
        backref="borrow_records"
    )

# -----------------------------
# Calculate Fine
# -----------------------------
    def calculate_fine(self):

        if (
            self.return_date
            and self.due_date
            and self.return_date > self.due_date
        ):

            days = (
                self.return_date -
                self.due_date
            ).days

            self.fine_amount = (
                days * 5000
            )

            return self.fine_amount

        self.fine_amount = 0
        return 0

# -----------------------------
# Return Book
# -----------------------------
    def update_return(self):

        self.return_date = (
            datetime.today().date()
        )

        self.status = "Returned"

        self.calculate_fine()

# -----------------------------
# Borrow History
# -----------------------------
    @staticmethod
    def get_user_borrow_history(
        user_id
    ):
        return BorrowRecord.query.filter_by(
            user_id=user_id
        ).order_by(
            BorrowRecord.borrow_date.desc()
        ).all()


# =================================================
# NOTIFICATION
# =================================================

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

# -----------------------------
# Mark Notification
# -----------------------------
    def mark_as_read(self):
        self.is_read = True


# -----------------------------
# User Notifications
# -----------------------------
    @staticmethod
    def get_user_notifications(
        user_id
    ):
        return Notification.query.filter_by(
            user_id=user_id
        ).order_by(
            Notification.created_at.desc()
        ).all()