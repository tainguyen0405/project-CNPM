from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Book, BorrowRecord
from datetime import date, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ─── TRANG CHỦ ───────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('login'))

# ─── ĐĂNG NHẬP ───────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Sai tên đăng nhập hoặc mật khẩu!')
    return render_template('login.html')

# ─── ĐĂNG XUẤT ───────────────────────────────────────
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ─── DASHBOARD ───────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    total_books   = Book.query.count()
    total_users   = User.query.count()
    total_borrow  = BorrowRecord.query.filter_by(return_date=None).count()
    overdue       = BorrowRecord.query.filter(
                        BorrowRecord.return_date == None,
                        BorrowRecord.due_date < date.today()
                    ).count()
    return render_template('dashboard.html',
        total_books=total_books,
        total_users=total_users,
        total_borrow=total_borrow,
        overdue=overdue
    )

# ─── QUẢN LÝ SÁCH ────────────────────────────────────
@app.route('/books')
@login_required
def books():
    query = request.args.get('q', '')
    if query:
        all_books = Book.query.filter(
            Book.title.contains(query) | Book.author.contains(query)
        ).all()
    else:
        all_books = Book.query.all()
    return render_template('books.html', books=all_books, query=query)

@app.route('/books/add', methods=['POST'])
@login_required
def add_book():
    b = Book(
        title    = request.form['title'],
        author   = request.form['author'],
        category = request.form['category'],
        quantity = int(request.form['quantity'])
    )
    db.session.add(b)
    db.session.commit()
    flash('Thêm sách thành công!')
    return redirect(url_for('books'))

@app.route('/books/delete/<int:id>')
@login_required
def delete_book(id):
    b = Book.query.get_or_404(id)
    db.session.delete(b)
    db.session.commit()
    flash('Đã xóa sách!')
    return redirect(url_for('books'))

# ─── MƯỢN / TRẢ ──────────────────────────────────────
@app.route('/borrow')
@login_required
def borrow():
    records = BorrowRecord.query.filter_by(return_date=None).all()
    books   = Book.query.filter(Book.quantity > 0).all()
    users   = User.query.filter_by(role='reader').all()
    return render_template('borrow.html',
        records=records, books=books, users=users, today=date.today()
    )

@app.route('/borrow/add', methods=['POST'])
@login_required
def add_borrow():
    r = BorrowRecord(
        user_id     = int(request.form['user_id']),
        book_id     = int(request.form['book_id']),
        borrow_date = date.today(),
        due_date    = date.today() + timedelta(days=14)
    )
    book = Book.query.get(int(request.form['book_id']))
    book.quantity -= 1
    db.session.add(r)
    db.session.commit()
    flash('Cho mượn thành công!')
    return redirect(url_for('borrow'))

@app.route('/borrow/return/<int:id>')
@login_required
def return_book(id):
    r = BorrowRecord.query.get_or_404(id)
    r.return_date = date.today()
    r.book.quantity += 1
    db.session.commit()
    flash('Trả sách thành công!')
    return redirect(url_for('borrow'))

# ─── KHỞI ĐỘNG ───────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(
                username = 'admin',
                password = generate_password_hash('admin123',method='pbkdf2:sha256'),
                role     = 'admin'
            ))
            db.session.add(User(
                username = 'reader1',
                password = generate_password_hash('reader123',method='pbkdf2:sha256'),
                role     = 'reader'
            ))
            db.session.commit()
            print("✅ Đã tạo tài khoản mặc định")
    app.run(debug=True)