from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

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

from datetime import (
    date,
    timedelta,
    datetime
)

from models import (
    db,
    User,
    LibrarianStaff,
    Category,
    Book,
    BorrowRecord,
    Notification
)


# ==================================================
# APP CONFIG
# ==================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "library_secret_key"

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///library.db"

db.init_app(app)

@app.route("/dashboard")
@login_required
def dashboard():

    total_books = Book.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    total_borrow = BorrowRecord.query.filter_by(
        status="Borrowing"
    ).count()

    overdue = BorrowRecord.query.filter(
        BorrowRecord.status == "Borrowing",
        BorrowRecord.due_date < date.today()
    ).count()

    total_notifications = Notification.query.count()

    return render_template(
        "dashboard.html",
        total_books=total_books,
        total_users=total_users,
        total_categories=total_categories,
        total_borrow=total_borrow,
        overdue=overdue,
        total_notifications=total_notifications
    )   

@app.route("/users")
@login_required
def users():

    if current_user.role != "admin":
        flash("Access denied")
        return redirect(
            url_for("dashboard")
        )

    data = User.query.all()

    return render_template(
        "users.html",
        users=data
    )

# ==================================================
# LOGIN MANAGER
# ==================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# ==================================================
# HOME
# ==================================================

@app.route("/")
def index():

    return redirect(
        url_for("login")
    )


# ==================================================
# LOGIN
# ==================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            flash(
                f"Welcome {user.full_name}"
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid username or password"
        )

    return render_template(
        "login.html"
    )


# ==================================================
# REGISTER
# ==================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        password = request.form["password"]

        # Kiểm tra username
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("register"))

        # Kiểm tra email
        if User.query.filter_by(email=email).first():
            flash("Email already exists.")
            return redirect(url_for("register"))

        new_user = User(
            full_name=full_name,
            username=username,
            email=email,
            phone=phone,
            address=address,
            role="student"
        )

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully. Please login.")

        return redirect(url_for("login"))

    return render_template("register.html")

# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


# ==================================================
# PROFILE
# ==================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
@login_required
def profile():

    if request.method == "POST":

        current_user.full_name = request.form[
            "full_name"
        ]

        current_user.email = request.form[
            "email"
        ]

        current_user.phone = request.form[
            "phone"
        ]

        current_user.address = request.form[
            "address"
        ]

        db.session.commit()

        flash(
            "Profile updated"
        )

    return render_template(
        "profile.html",
        user=current_user
    )


# ==================================================
# CHANGE PASSWORD
# ==================================================

@app.route(
    "/change-password",
    methods=["GET", "POST"]
)
@login_required
def change_password():

    if request.method == "POST":

        old_password = request.form[
            "old_password"
        ]

        new_password = request.form[
            "new_password"
        ]

        if not check_password_hash(
            current_user.password,
            old_password
        ):

            flash(
                "Old password incorrect"
            )

            return redirect(
                url_for(
                    "change_password"
                )
            )

        current_user.password = (
            generate_password_hash(
                new_password
            )
        )

        db.session.commit()

        flash(
            "Password changed"
        )

        return redirect(
            url_for("profile")
        )

    return render_template(
        "change_password.html"
    )
    # ==================================================
# CATEGORY MANAGEMENT
# ==================================================

@app.route("/categories")
@login_required
def categories():

    data = Category.query.all()

    return render_template(
        "categories.html",
        categories=data
    )


@app.route(
    "/categories/add",
    methods=["POST"]
)
@login_required
def add_category():

    category = Category(
        name=request.form["name"],
        description=request.form.get(
            "description"
        )
    )

    db.session.add(category)
    db.session.commit()

    flash("Category added")

    return redirect(
        url_for("categories")
    )


@app.route(
    "/categories/update/<int:id>",
    methods=["POST"]
)
@login_required
def update_category(id):

    category = Category.query.get_or_404(id)

    category.name = request.form["name"]
    category.description = request.form.get(
        "description"
    )

    db.session.commit()

    flash("Category updated")

    return redirect(
        url_for("categories")
    )


@app.route(
    "/categories/delete/<int:id>"
)
@login_required
def delete_category(id):

    category = Category.query.get_or_404(id)

    db.session.delete(category)
    db.session.commit()

    flash("Category deleted")

    return redirect(
        url_for("categories")
    )


# ==================================================
# BOOK MANAGEMENT
# ==================================================

@app.route("/books")
@login_required
def books():

    keyword = request.args.get(
        "q",
        ""
    )

    if keyword:

        data = Book.query.filter(
            Book.title.contains(keyword)
        ).all()

    else:

        data = Book.query.all()

    categories = Category.query.all()

    return render_template(
        "books.html",
        books=data,
        categories=categories,
        query=keyword
    )

# ==================================================
# ADD BOOK
# ==================================================

@app.route(
    "/books/add",
    methods=["POST"]
)
@login_required
def add_book():

    quantity = int(
        request.form["quantity"]
    )

    book = Book(

        isbn=request.form.get("isbn"),

        title=request.form["title"],

        author=request.form.get(
            "author"
        ),

        publisher=request.form.get(
            "publisher"
        ),

        publish_year=request.form.get(
            "publish_year"
        ),

        quantity=quantity,

        available_copies=quantity,

        category_id=int(
            request.form["category_id"]
        )
    )

    db.session.add(book)
    db.session.commit()

    flash("Book added")

    return redirect(
        url_for("books")
    )

# ==================================================
# BOOK DETAIL
# ==================================================

@app.route("/books/<int:id>")
@login_required
def book_detail(id):

    book = Book.query.get_or_404(id)

    return render_template(
        "book_detail.html",
        book=book
    )

# ==================================================
# UPDATE BOOK
# ==================================================

@app.route(
    "/books/update/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def update_book(id):

    book = Book.query.get_or_404(id)

    if request.method == "POST":

        book.isbn = request.form.get(
            "isbn"
        )

        book.title = request.form[
            "title"
        ]

        book.author = request.form.get(
            "author"
        )

        book.publisher = request.form.get(
            "publisher"
        )

        year = request.form.get(
            "publish_year"
        )

        if year:
            book.publish_year = int(year)

        quantity = int(
            request.form["quantity"]
        )

        book.quantity = quantity
        book.available_copies = quantity

        category_id = request.form.get(
            "category_id"
        )

        if category_id:
            book.category_id = int(
                category_id
            )

        db.session.commit()

        flash("Book updated")

        return redirect(
            url_for("books")
        )

    categories = Category.query.all()

    return render_template(
        "update_book.html",
        book=book,
        categories=categories
    )

# ==================================================
# DELETE BOOK
# ==================================================

@app.route(
    "/books/delete/<int:id>"
)
@login_required
def delete_book(id):

    book = Book.query.get_or_404(id)

    db.session.delete(book)
    db.session.commit()

    flash("Book deleted")

    return redirect(
        url_for("books")
    )
    # ==================================================
# BORROW MANAGEMENT
# ==================================================

@app.route("/borrow")
@login_required
def borrow():

    records = BorrowRecord.query.filter_by(
        status="Borrowing"
    ).all()

    users = User.query.filter_by(
        role="reader"
    ).all()

    books = Book.query.filter(
        Book.available_copies > 0
    ).all()

    return render_template(
        "borrow.html",
        records=records,
        users=users,
        books=books,
        today=date.today()
    )


# --------------------------------------------------

@app.route(
    "/borrow/add",
    methods=["POST"]
)
@login_required
def add_borrow():

    user_id = int(
        request.form["user_id"]
    )

    book_id = int(
        request.form["book_id"]
    )

    book = Book.query.get_or_404(
        book_id
    )

    if book.available_copies <= 0:

        flash(
            "Book unavailable"
        )

        return redirect(
            url_for("borrow")
        )

    record = BorrowRecord(

        user_id=user_id,

        book_id=book_id,

        borrow_date=date.today(),

        due_date=
        date.today()
        + timedelta(days=14),

        status="Borrowing"
    )

    book.quantity -= 1
    book.available_copies -= 1

    notification = Notification(

        user_id=user_id,

        message=
        f'You borrowed "{book.title}"'
    )

    db.session.add(record)
    db.session.add(notification)

    db.session.commit()

    flash(
        "Borrow successfully"
    )

    return redirect(
        url_for("borrow")
    )


# --------------------------------------------------

@app.route(
    "/borrow/return/<int:id>"
)
@login_required
def return_book(id):

    record = BorrowRecord.query.get_or_404(
        id
    )

    record.return_date = date.today()

    record.status = "Returned"

    record.book.quantity += 1
    record.book.available_copies += 1

    fine = record.calculate_fine()

    record.fine_amount = fine

    notification = Notification(

        user_id=record.user_id,

        message=
        f'You returned "{record.book.title}"'
    )

    db.session.add(notification)

    db.session.commit()

    flash(
        "Return successfully"
    )

    return redirect(
        url_for("borrow")
    )


# --------------------------------------------------

@app.route(
    "/borrow/fine/<int:id>"
)
@login_required
def fine(id):

    record = BorrowRecord.query.get_or_404(
        id
    )

    amount = record.calculate_fine()

    record.fine_amount = amount

    db.session.commit()

    return render_template(
        "fine.html",
        record=record
    )


# ==================================================
# NOTIFICATION MANAGEMENT
# ==================================================

@app.route("/notifications")
@login_required
def notifications():

    data = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return render_template(
        "notifications.html",
        notifications=data
    )


# --------------------------------------------------

@app.route(
    "/notifications/read/<int:id>"
)
@login_required
def mark_notification(id):

    notification = Notification.query.get_or_404(
        id
    )

    notification.is_read = True

    db.session.commit()

    flash(
        "Notification marked as read"
    )

    return redirect(
        url_for("notifications")
    )


# ==================================================
# REPORT MANAGEMENT
# ==================================================

@app.route("/reports")
@login_required
def reports():

    if current_user.role not in [
        "admin",
        "librarian"
    ]:

        flash(
            "Access denied"
        )

        return redirect(
            url_for("dashboard")
        )

    report = {

        "books":
        Book.query.count(),

        "users":
        User.query.count(),

        "categories":
        Category.query.count(),

        "borrow":
        BorrowRecord.query.count(),

        "returned":
        BorrowRecord.query.filter_by(
            status="Returned"
        ).count(),

        "overdue":
        BorrowRecord.query.filter(
            BorrowRecord.status == "Borrowing",
            BorrowRecord.due_date < date.today()
        ).count()
    }

    return render_template(
        "reports.html",
        report=report
    )


# ==================================================
# CREATE DEFAULT DATA
# ==================================================

def create_default_data():

    admin = User.query.filter_by(
        username="admin"
    ).first()

    if not admin:

        admin = User(
            full_name="Administrator",
            username="admin",
            email="admin@gmail.com",
            phone="0123456789",
            address="Library Office",
            password=
            generate_password_hash(
                "admin123"
            ),
            role="admin"
        )

        db.session.add(admin)

    librarian = User.query.filter_by(
        username="librarian"
    ).first()

    if not librarian:

        librarian = User(
            full_name="Library Staff",
            username="librarian",
            email="staff@gmail.com",
            phone="0111111111",
            address="Library",
            password=
            generate_password_hash(
                "staff123"
            ),
            role="librarian"
        )

        db.session.add(
            librarian
        )

        db.session.flush()

        staff = LibrarianStaff(
            user_id=librarian.id,
            employee_code="LIB001"
        )

        db.session.add(staff)
    
        # ===============================
    # STUDENT
    # ===============================

    student = User.query.filter_by(
        username="student"
    ).first()

    if not student:

        student = User(
            full_name="Student",
            username="student",
            email="student@gmail.com",
            phone="0999999999",
            address="Student Dormitory",
            password=generate_password_hash("student123"),
            role="reader"
        )

        db.session.add(student)

    # ===============================
    # CATEGORY
    # ===============================

    if Category.query.count() == 0:

        categories = [

            Category(
                name="Programming",
                description="Programming books"
            ),

            Category(
                name="Database",
                description="Database books"
            ),

            Category(
                name="Software Engineering",
                description="Software engineering books"
            ),

            Category(
                name="Networking",
                description="Networking books"
            )
        ]

        db.session.add_all(categories)

    db.session.commit()


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_default_data()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )