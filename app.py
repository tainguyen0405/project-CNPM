from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import date, timedelta

from models import (
    db,
    User,
    Category,
    Book,
    BorrowRecord,
    Notification
)

# ==========================================
# APP CONFIG
# ==========================================

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)

# ==========================================
# LOGIN MANAGER
# ==========================================

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ==========================================
# HOME
# ==========================================

@app.route('/')
def index():
    return redirect(url_for('login'))


# ==========================================
# LOGIN
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):
            login_user(user)

            return redirect(
                url_for('dashboard')
            )

        flash('Sai tên đăng nhập hoặc mật khẩu')

    return render_template('login.html')


# ==========================================
# LOGOUT
# ==========================================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(
        url_for('login')
    )


# ==========================================
# DASHBOARD
# ==========================================

@app.route('/dashboard')
@login_required
def dashboard():

    total_books = Book.query.count()

    total_users = User.query.count()

    total_categories = Category.query.count()

    total_borrow = BorrowRecord.query.filter_by(
        return_date=None
    ).count()

    overdue = BorrowRecord.query.filter(
        BorrowRecord.return_date == None,
        BorrowRecord.due_date < date.today()
    ).count()

    total_notifications = Notification.query.count()

    return render_template(
        'dashboard.html',
        total_books=total_books,
        total_users=total_users,
        total_categories=total_categories,
        total_borrow=total_borrow,
        overdue=overdue,
        total_notifications=total_notifications
    )


# ==========================================
# CATEGORY MANAGEMENT
# ==========================================

@app.route('/categories')
@login_required
def categories():

    data = Category.query.all()

    return render_template(
        'categories.html',
        categories=data
    )


@app.route('/categories/add', methods=['POST'])
@login_required
def add_category():

    category = Category(
        name=request.form['name']
    )

    db.session.add(category)

    db.session.commit()

    flash('Thêm thể loại thành công')

    return redirect(
        url_for('categories')
    )


# ==========================================
# BOOK MANAGEMENT
# ==========================================

@app.route('/books')
@login_required
def books():

    query = request.args.get(
        'q',
        ''
    )

    if query:

        all_books = Book.query.filter(
            Book.title.contains(query)
        ).all()

    else:

        all_books = Book.query.all()

    categories = Category.query.all()

    return render_template(
        'books.html',
        books=all_books,
        categories=categories,
        query=query
    )


@app.route('/books/add', methods=['POST'])
@login_required
def add_book():

    book = Book(
        title=request.form['title'],
        author=request.form['author'],
        quantity=int(
            request.form['quantity']
        ),
        category_id=int(
            request.form['category_id']
        )
    )

    db.session.add(book)

    db.session.commit()

    flash('Thêm sách thành công')

    return redirect(
        url_for('books')
    )


@app.route('/books/delete/<int:id>')
@login_required
def delete_book(id):

    book = Book.query.get_or_404(id)

    db.session.delete(book)

    db.session.commit()

    flash('Đã xóa sách')

    return redirect(
        url_for('books')
    )


# ==========================================
# BORROW MANAGEMENT
# ==========================================

@app.route('/borrow')
@login_required
def borrow():

    records = BorrowRecord.query.filter_by(
        return_date=None
    ).all()

    users = User.query.filter_by(
        role='reader'
    ).all()

    books = Book.query.filter(
        Book.quantity > 0
    ).all()

    return render_template(
        'borrow.html',
        records=records,
        users=users,
        books=books,
        today=date.today()
    )


@app.route('/borrow/add', methods=['POST'])
@login_required
def add_borrow():

    user_id = int(
        request.form['user_id']
    )

    book_id = int(
        request.form['book_id']
    )

    record = BorrowRecord(
        user_id=user_id,
        book_id=book_id,
        borrow_date=date.today(),
        due_date=date.today() + timedelta(days=14)
    )

    book = Book.query.get(book_id)

    if book.quantity <= 0:

        flash('Sách đã hết')

        return redirect(
            url_for('borrow')
        )

    book.quantity -= 1

    db.session.add(record)

    notification = Notification(
        user_id=user_id,
        message=f'Bạn đã mượn sách "{book.title}"'
    )

    db.session.add(notification)

    db.session.commit()

    flash('Cho mượn thành công')

    return redirect(
        url_for('borrow')
    )


@app.route('/borrow/return/<int:id>')
@login_required
def return_book(id):

    record = BorrowRecord.query.get_or_404(id)

    record.return_date = date.today()

    record.book.quantity += 1

    db.session.commit()

    flash('Trả sách thành công')

    return redirect(
        url_for('borrow')
    )


# ==========================================
# NOTIFICATION
# ==========================================

@app.route('/notifications')
@login_required
def notifications():

    data = Notification.query.order_by(
        Notification.created_at.desc()
    ).all()

    return render_template(
        'notifications.html',
        notifications=data
    )


# ==========================================
# DATABASE INIT
# ==========================================

def create_default_data():

    if not User.query.filter_by(
        username='admin'
    ).first():

        admin = User(
            full_name='Administrator',
            username='admin',
            email='admin@gmail.com',
            phone='0123456789',
            address='Library Office',
            password=generate_password_hash(
                'admin123'
            ),
            role='admin'
        )

        reader = User(
            full_name='Reader One',
            username='reader1',
            email='reader1@gmail.com',
            phone='0988888888',
            address='Student Dormitory',
            password=generate_password_hash(
                'reader123'
            ),
            role='reader'
        )

        db.session.add(admin)
        db.session.add(reader)

    if Category.query.count() == 0:

        categories = [
            Category(name='Programming'),
            Category(name='Database'),
            Category(name='Networking'),
            Category(name='Software Engineering')
        ]

        db.session.add_all(categories)

    db.session.commit()

# ==========================================
# RUN
# ==========================================

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

        create_default_data()

    app.run(
        debug=True
    )