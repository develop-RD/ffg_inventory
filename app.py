from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid


app = Flask(__name__)
app.config["SECRET_KEY"] = (
    "2079acc5744b8f1fe9b9c84cb9a7a21ed531bbca08574b035a2bf52f4bf6cbe7"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    items = db.relationship(
        "InventoryItem", backref="user", lazy=True, cascade="all, delete-orphan"
    )


class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)
    image_path = db.Column(db.String(255))
    description = db.Column(db.Text)
    pros = db.Column(db.Text)
    cons = db.Column(db.Text)
    rating = db.Column(db.Integer)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/users/search")
@login_required
def user_search():
    query = request.args.get("q", "")
    users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    return render_template("users.html", users=users, search_query=query)


@app.route("/users")
@login_required
def user_list():
    users = User.query.order_by(User.username).all()
    return render_template("users.html", users=users)


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("my_profile"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Заполните все поля")
            return redirect(url_for("login"))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("my_profile"))

        flash("Неверное имя пользователя или пароль")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Имя пользователя уже занято")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("my_profile"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/myprofile")
@login_required
def my_profile():
    return redirect(url_for("view_profile", username=current_user.username))


@app.route("/profile/<username>")
def view_profile(username):
    viewed_user = User.query.filter_by(username=username).first_or_404()
    items = InventoryItem.query.filter_by(user_id=viewed_user.id).all()

    inventory = {
        "gorget": next((i for i in items if i.item_type == "gorget"), None),
        "lokti": next((i for i in items if i.item_type == "lokti"), None),
        "bag": next((i for i in items if i.item_type == "bag"), None),
        "namasnik": next((i for i in items if i.item_type == "namasnik"), None),
        "head": next((i for i in items if i.item_type == "head"), None),
        "naplech": next((i for i in items if i.item_type == "naplech"), None),
        "sword1": next((i for i in items if i.item_type == "sword1"), None),
        "sword2": next((i for i in items if i.item_type == "sword2"), None),
        "sword3": next((i for i in items if i.item_type == "sword3"), None),
        "sht": next((i for i in items if i.item_type == "sht"), None),
        "torso": next((i for i in items if i.item_type == "torso"), None),
        "ng": next((i for i in items if i.item_type == "ng"), None),
        "brass": next((i for i in items if i.item_type == "brass"), None),
        "gloves": next((i for i in items if i.item_type == "gloves"), None),
        "pants": next((i for i in items if i.item_type == "pants"), None),
        "shoes": next((i for i in items if i.item_type == "shoes"), None),
    }

    is_owner = current_user.is_authenticated and current_user.id == viewed_user.id
    return render_template(
        "profile.html", inventory=inventory, viewed_user=viewed_user, is_owner=is_owner
    )


@app.route("/upload/<item_type>", methods=["GET", "POST"])
@login_required
def upload(item_type):
    # проверяем данные из БД

    items = InventoryItem.query.filter_by(user_id=current_user.id).all()
    inventory = {
        "gorget": next((i for i in items if i.item_type == "gorget"), None),
        "lokti": next((i for i in items if i.item_type == "lokti"), None),
        "bag": next((i for i in items if i.item_type == "bag"), None),
        "namasnik": next((i for i in items if i.item_type == "namasnik"), None),
        "head": next((i for i in items if i.item_type == "head"), None),
        "naplech": next((i for i in items if i.item_type == "naplech"), None),
        "sword1": next((i for i in items if i.item_type == "sword1"), None),
        "sword2": next((i for i in items if i.item_type == "sword2"), None),
        "sword3": next((i for i in items if i.item_type == "sword3"), None),
        "sht": next((i for i in items if i.item_type == "sht"), None),
        "torso": next((i for i in items if i.item_type == "torso"), None),
        "ng": next((i for i in items if i.item_type == "ng"), None),
        "brass": next((i for i in items if i.item_type == "brass"), None),
        "gloves": next((i for i in items if i.item_type == "gloves"), None),
        "pants": next((i for i in items if i.item_type == "pants"), None),
        "shoes": next((i for i in items if i.item_type == "shoes"), None),
    }
    if request.method == "POST":
        file = request.files["image"]
        if file and allowed_file(file.filename):
            filename = secure_filename(
                f"{current_user.id}_{item_type}.{file.filename.rsplit('.', 1)[1].lower()}"
            )
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            print(filename)

        item = InventoryItem.query.filter_by(
            user_id=current_user.id, item_type=item_type
        ).first()
        if not item:
            item = InventoryItem(
                user_id=current_user.id,
                item_type=item_type,
                image_path=filename,
                description=request.form["description"],
                pros=request.form["pros"],
                cons=request.form["cons"],
                rating=int(request.form["rating"]),
            )
            db.session.add(item)
        else:
            if item.image_path:
                old_file = os.path.join(app.config["UPLOAD_FOLDER"], item.image_path)
                # if os.path.exists(old_file):
                #    os.remove(old_file)
            item.image_path = item.image_path
            item.description = request.form["description"]
            item.pros = request.form["pros"]
            item.cons = request.form["cons"]
            item.rating = int(request.form["rating"])

        db.session.commit()
        return redirect(url_for("my_profile"))

    return render_template("upload.html", item_type=item_type, inventory=inventory)


@app.route("/delete/<item_type>", methods=["POST"])
@login_required
def delete_item(item_type):
    item = InventoryItem.query.filter_by(
        user_id=current_user.id, item_type=item_type
    ).first()
    if item:
        if item.image_path:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], item.image_path)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(item)
        db.session.commit()
        flash("Предмет удален", "success")

    return redirect(url_for("my_profile"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])
    app.run(debug=True)
