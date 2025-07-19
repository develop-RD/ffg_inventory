from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, date  # Добавьте в начало файла

app = Flask(__name__)
app.config["SECRET_KEY"] = "2079acc5744b8f1fe9b9c84cb9a7a21ed531bbca08574b035a2bf52f4bf6cbe7"
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
    weapon_class = db.Column(db.String(20), default='sword_buckler')
    age = db.Column(db.Integer)
    # Оружие и стаж
    has_longsword = db.Column(db.Boolean, default=False)
    longsword_since = db.Column(db.Date)
    has_rapier = db.Column(db.Boolean, default=False)
    rapier_since = db.Column(db.Date)
    has_sabre = db.Column(db.Boolean, default=False)
    sabre_since = db.Column(db.Date)
    has_sword_buckler = db.Column(db.Boolean, default=False)
    sword_buckler_since = db.Column(db.Date)
    items = db.relationship(
        "InventoryItem", backref="user", lazy=True, cascade="all, delete-orphan"
    )


class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    weapon_class = db.Column(db.String(20), default='all')  # 'all' или конкретный класс
    item_type = db.Column(db.String(20), nullable=False)
    image_paths = db.Column(db.Text)
    description = db.Column(db.Text)
    pros = db.Column(db.Text)
    cons = db.Column(db.Text)
    rating = db.Column(db.Integer)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


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



@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    weapon_data = [
        {'name': 'Длинный меч', 'field': 'longsword', 'has': current_user.has_longsword, 'since': current_user.longsword_since},
        {'name': 'Рапира', 'field': 'rapier', 'has': current_user.has_rapier, 'since': current_user.rapier_since},
        {'name': 'Сабля', 'field': 'sabre', 'has': current_user.has_sabre, 'since': current_user.sabre_since},
        {'name': 'Меч и баклер', 'field': 'sword_buckler', 'has': current_user.has_sword_buckler, 'since': current_user.sword_buckler_since}
    ]

    if request.method == "POST":
        current_user.age = request.form.get("age") or None
        
        for weapon in weapon_data:
            has_field = f"has_{weapon['field']}"
            since_field = f"{weapon['field']}_since"
            
            has_weapon = request.form.get(has_field) == 'on'
            setattr(current_user, has_field, has_weapon)
            
            if has_weapon:
                since_date = request.form.get(since_field)
                if since_date:
                    setattr(current_user, since_field, datetime.strptime(since_date, '%Y-%m-%d').date())
                else:
                    setattr(current_user, since_field, None)
            else:
                setattr(current_user, since_field, None)
        
        db.session.commit()
        flash("Профиль успешно обновлен", "success")
        return redirect(url_for("view_profile", username=current_user.username))
    
    return render_template("edit_profile.html", weapon_data=weapon_data)

@app.route("/profile/<username>")
def view_profile(username):
    viewed_user = User.query.filter_by(username=username).first_or_404()
    weapon_class = request.args.get('weapon_class', viewed_user.weapon_class)
    
    # Получаем предметы для текущего класса оружия и общие предметы
    items = InventoryItem.query.filter_by(user_id=viewed_user.id).filter(
        (InventoryItem.weapon_class == weapon_class) | (InventoryItem.weapon_class == 'all')
    ).all()
    # Подготавливаем данные об оружии для шаблона
    weapon_data = [
        {'name': 'Длинный меч', 'field': 'longsword', 'has': viewed_user.has_longsword, 'since': viewed_user.longsword_since},
        {'name': 'Рапира', 'field': 'rapier', 'has': viewed_user.has_rapier, 'since': viewed_user.rapier_since},
        {'name': 'Сабля', 'field': 'sabre', 'has': viewed_user.has_sabre, 'since': viewed_user.sabre_since},
        {'name': 'Меч и баклер', 'field': 'sword_buckler', 'has': viewed_user.has_sword_buckler, 'since': viewed_user.sword_buckler_since}
    ]

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
    "profile.html", 
    inventory=inventory, 
    viewed_user=viewed_user, 
    is_owner=is_owner,
    current_weapon_class=weapon_class,
    weapon_data=weapon_data,
    datetime=datetime  # передаем модуль datetime для вычисления стажа
    ) 

@app.route("/set_weapon_class", methods=["POST"])
@login_required
def set_weapon_class():
    weapon_class = request.form.get("weapon_class")
    if weapon_class in ["sword_buckler", "longsword", "rapier_dagger", "sabre"]:
        current_user.weapon_class = weapon_class
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid weapon class"})



# Обработчик загрузки/редактирования
# Обработчик загрузки/редактирования
@app.route("/upload/<item_type>", methods=["GET", "POST"])
@login_required
def upload(item_type):
    weapon_class = request.args.get('weapon_class', current_user.weapon_class)
    item = InventoryItem.query.filter_by(
        user_id=current_user.id,
        item_type=item_type,
        weapon_class=weapon_class
    ).first()

    if request.method == "POST":
        # Обработка изображений
        image_paths = []
        
        # Если редактирование - обрабатываем удаление
        if item and item.image_paths:
            current_images = item.image_paths.split(',')
            delete_images = request.form.getlist('delete_images')
            
            # Удаляем отмеченные файлы
            for img in delete_images:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img))
                except OSError:
                    pass
            
            # Оставляем неотмеченные
            image_paths = [img for img in current_images if img not in delete_images]

        # Обрабатываем новые изображения
        files = request.files.getlist('images')
        for i, file in enumerate(files):
            if len(image_paths) >= 5:
                break
                
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(
                    f"{current_user.id}_{weapon_class}_{item_type}_{len(image_paths)}.{file.filename.rsplit('.', 1)[1].lower()}"
                )
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                image_paths.append(filename)

        # Создаем или обновляем запись
        if not item:
            item = InventoryItem(
                user_id=current_user.id,
                weapon_class=weapon_class,
                item_type=item_type,
                image_paths=",".join(image_paths),
                description=request.form.get("description", ""),
                pros=request.form.get("pros", ""),
                cons=request.form.get("cons", ""),
                rating=int(request.form.get("rating", 3)),
            )
            db.session.add(item)
        else:
            item.image_paths = ",".join(image_paths) if image_paths else ""
            item.description = request.form.get("description", "")
            item.pros = request.form.get("pros", "")
            item.cons = request.form.get("cons", "")
            item.rating = int(request.form.get("rating", 3))

        db.session.commit()
        return redirect(url_for("view_profile", username=current_user.username, weapon_class=weapon_class))

    return render_template(
        "upload.html",
        item_type=item_type,
        weapon_class=weapon_class,
        item=item
    )

# Обработчик удаления предмета
@app.route("/delete/<item_type>", methods=["POST"])
@login_required
def delete_item(item_type):
    weapon_class = request.args.get('weapon_class', current_user.weapon_class)
    item = InventoryItem.query.filter_by(
        user_id=current_user.id,
        item_type=item_type,
        weapon_class=weapon_class
    ).first_or_404()

    # Удаляем все изображения
    if item.image_paths:
        for image_path in item.image_paths.split(','):
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_path))
            except OSError:
                pass

    # Удаляем запись из БД
    db.session.delete(item)
    db.session.commit()
    flash("Предмет удален", "success")
    return redirect(url_for("view_profile", username=current_user.username, weapon_class=weapon_class))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])
    app.run(debug=True)
