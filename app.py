from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, date
# для указания стажа
from dateutil.relativedelta import relativedelta

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
    weapon_class = db.Column(db.String(20), default="sword_buckler")
    age = db.Column(db.Integer)
    real_name = db.Column(db.String(100))
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
    model = db.Column(db.String(20), default="none")  # изготовитель
    model_site = db.Column(db.Text)  # ссылка на изготовителя
    weapon_class = db.Column(db.String(20), default="all")  # 'all' или конкретный класс
    item_type = db.Column(db.String(20), nullable=False)
    image_paths = db.Column(db.Text)
    description = db.Column(db.Text)
    pros = db.Column(db.Text)
    cons = db.Column(db.Text)
    rating = db.Column(db.Integer)
    # поля для оружия
    weight = db.Column(db.Float)  # вес
    length = db.Column(db.Float)  # длина
    balance_point = db.Column(db.Float)  # точка баланса
    point_perimeter = db.Column(db.Float)  # периметр пунты
    stiffness = db.Column(db.Float)  # жесткость


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


@app.route("/search")
@login_required
def user_search_equip():
       # Получаем параметры поиска из запроса
    manufacturer = request.args.get("manufacturer", "")
    item_type = request.args.get("item_type", "")
    weapon_class = request.args.get("weapon_class", "all")
    rating_item = request.args.get("rating", "")
    users = User.query.order_by(User.username).all()
    results = []
    
    for user in users:
        # Получаем все предметы пользователя, которые соответствуют критериям поиска
        query = InventoryItem.query.filter_by(user_id=user.id)
        
        if manufacturer:
            query = query.filter_by(model=manufacturer)
        
        if item_type:
            query = query.filter_by(item_type=item_type)
        
        if rating_item:
            query = query.filter_by(rating=rating_item)

        print(rating_item)
        if weapon_class != "all":
            query = query.filter(
                (InventoryItem.weapon_class == weapon_class) |
                (InventoryItem.weapon_class == "all")
            )
        items = query.all()
        
        if items:
            # Группируем предметы по классу оружия
            items_by_class = {}
            for item in items:
                if item.weapon_class not in items_by_class:
                    items_by_class[item.weapon_class] = []
                items_by_class[item.weapon_class].append(item)
            
            results.append({
                "user": user,
                "items_by_class": items_by_class
            })

    # Список типов предметов для формы поиска
    item_types = [
        "gorget", "head", "namasnik", "naplech", "torso", 
        "ng", "brass", "lokti", "gloves", "sht", 
        "pants", "shoes", "bag", "sword1", "sword2", "sword3"
    ]
    
    return render_template(
        "search.html",
        results=results,
        search_manufacturer=manufacturer,
        search_item_type=item_type,
        search_weapon_class=weapon_class,
        weapon_classes={
            "sword_buckler": "Меч и баклер",
            "longsword": "Длинный меч",
            "rapier_dagger": "Рапира и дага",
            "sabre": "Сабля",
            "all": "Все классы"
        },
        manufacturers=[
            ("Kvetun", "Кветунь"),
            ("Gold_Sokol", "Золотой сокол"),
            ("PBT", "PBT"),
            ("SPES", "SPES"),
            ("Foxtail", "Fox Tail"),
            ("Fencing_shop", "Fencing shop"),
            ("pangolins", "Панголины"),
            ("Raidu", "Raidu"),
            ("under_cover", "Under Cover"),
            ("ultima_ratio", "Ultima Ratio"),
            ("raven_blade", "RavenBlade"),
            ("PikeArmory", "Pike Armory")
        ],
        rating=[1,2,3,4,5],
        search_rating=rating_item,
        item_types=item_types
    ) 

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
@login_required
def view_profile(username):
    viewed_user = User.query.filter_by(username=username).first_or_404()
    weapon_class = request.args.get("weapon_class", viewed_user.weapon_class)

    # Получаем предметы для текущего класса оружия и общие предметы
    items = (
        InventoryItem.query.filter_by(user_id=viewed_user.id)
        .filter(
            (InventoryItem.weapon_class == weapon_class)
            | (InventoryItem.weapon_class == "all")
        )
        .all()
    )

    # Подготавливаем данные об оружии с расчетом стажа
    weapon_data = []
    today = date.today()

    weapons = [
        ("longsword", "Длинный меч"),
        ("rapier", "Рапира"),
        ("sabre", "Сабля"),
        ("sword_buckler", "Меч и баклер"),
    ]

    for field, name in weapons:
        has_weapon = getattr(viewed_user, f"has_{field}")
        since_date = getattr(viewed_user, f"{field}_since")
        experience = None

        if has_weapon and since_date:
            delta = relativedelta(today, since_date)
            experience = {"years": delta.years, "months": delta.months}

        weapon_data.append(
            {
                "name": name,
                "field": field,
                "has": has_weapon,
                "since": since_date,
                "experience": experience,
            }
        )

    # Формируем инвентарь
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
        datetime=datetime,  # передаем модуль datetime для шаблона
    )


@app.route("/edit_profile/", methods=["GET", "POST"])
@login_required
def edit_profile():
    # Подготовка данных об оружии (аналогично view_profile)
    weapon_data = []
    today = date.today()

    weapons = [
        ("longsword", "Длинный меч"),
        ("rapier", "Рапира"),
        ("sabre", "Сабля"),
        ("sword_buckler", "Меч и баклер"),
    ]

    for field, name in weapons:
        has_weapon = getattr(current_user, f"has_{field}")
        since_date = getattr(current_user, f"{field}_since")
        experience = None

        if has_weapon and since_date:
            delta = relativedelta(today, since_date)
            experience = {"years": delta.years, "months": delta.months}

        weapon_data.append(
            {
                "name": name,
                "field": field,
                "has": has_weapon,
                "since": since_date,
                "experience": experience,
            }
        )

    if request.method == "POST":
        try:
            current_user.real_name = request.form.get("real_name")
            current_user.age = (
                int(request.form.get("age")) if request.form.get("age") else None
            )

            for weapon in weapon_data:
                has_field = f"has_{weapon['field']}"
                since_field = f"{weapon['field']}_since"

                has_weapon = request.form.get(has_field) == "on"
                setattr(current_user, has_field, has_weapon)

                if has_weapon:
                    since_date_str = request.form.get(since_field)
                    if since_date_str:
                        since_date = datetime.strptime(
                            since_date_str, "%Y-%m-%d"
                        ).date()
                        setattr(current_user, since_field, since_date)
                    else:
                        # Если дата не указана, но оружие выбрано - устанавливаем текущую дату
                        setattr(current_user, since_field, today)
                else:
                    setattr(current_user, since_field, None)

            db.session.commit()
            flash("Профиль успешно обновлен", "success")
            return redirect(url_for("view_profile", username=current_user.username))
        except ValueError as e:
            flash(f"Ошибка в данных: {str(e)}", "error")

    return render_template("edit_profile.html", weapon_data=weapon_data)


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
@app.route("/upload/<item_type>", methods=["GET", "POST"])
@login_required
def upload(item_type):
    weapon_class = request.args.get("weapon_class", current_user.weapon_class)
    item = InventoryItem.query.filter_by(
        user_id=current_user.id, item_type=item_type, weapon_class=weapon_class
    ).first()

    if request.method == "POST":
        # Обработка изображений
        image_paths = []

        # Если редактирование - обрабатываем удаление
        if item and item.image_paths:
            current_images = item.image_paths.split(",")
            delete_images = request.form.getlist("delete_images")

            # Удаляем отмеченные файлы
            for img in delete_images:
                try:
                    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], img))
                except OSError:
                    pass

            # Оставляем неотмеченные
            image_paths = [img for img in current_images if img not in delete_images]

        # Обрабатываем новые изображения
        files = request.files.getlist("images")
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
                model=request.form.get("model", ""),
                model_site=request.form.get("model_site", ""),
                rating=int(request.form.get("rating", 3)),
                # Новые поля для оружия
                weight=float(request.form.get("weight", 0)) if item_type in ['sword1', 'sword2', 'sword3'] else None,
                length=float(request.form.get("length", 0)) if item_type in ['sword1', 'sword2', 'sword3'] else None,
                balance_point=float(request.form.get("balance_point", 0)) if item_type in ['sword1', 'sword2', 'sword3'] else None,
                point_perimeter=float(request.form.get("point_perimeter", 0)) if item_type in ['sword1', 'sword2', 'sword3'] else None,
                stiffness=request.form.get("stiffness", "") if item_type in ['sword1', 'sword2', 'sword3'] else None            
            )
            print(item.model)
            db.session.add(item)
        else:
            item.image_paths = ",".join(image_paths) if image_paths else ""
            item.description = request.form.get("description", "")
            item.pros = request.form.get("pros", "")
            item.cons = request.form.get("cons", "")
            item.rating = int(request.form.get("rating", 3))
            item.model = request.form.get("model", "")
            item.model_site = request.form.get("model_site", "")
            # Обновляем новые поля для оружия
            if item_type in ['sword1', 'sword2', 'sword3']:
                item.weight = float(request.form.get("weight", 0))
                item.length = float(request.form.get("length", 0))
                item.balance_point = float(request.form.get("balance_point", 0))
                item.point_perimeter = float(request.form.get("point_perimeter", 0))
                item.stiffness = request.form.get("stiffness", "")
            print("before", item.model)
        db.session.commit()
        return redirect(
            url_for(
                "view_profile",
                username=current_user.username,
                weapon_class=weapon_class,
            )
        )

    return render_template(
        "upload.html", item_type=item_type, weapon_class=weapon_class, item=item, is_weapon=item_type in ['sword1', 'sword2', 'sword3']  # Передаем флаг, что это оружие
    )


# Обработчик удаления предмета
@app.route("/delete/<item_type>", methods=["POST"])
@login_required
def delete_item(item_type):
    weapon_class = request.args.get("weapon_class", current_user.weapon_class)
    item = InventoryItem.query.filter_by(
        user_id=current_user.id, item_type=item_type, weapon_class=weapon_class
    ).first_or_404()

    # Удаляем все изображения
    if item.image_paths:
        for image_path in item.image_paths.split(","):
            try:
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], image_path))
            except OSError:
                pass

    # Удаляем запись из БД
    db.session.delete(item)
    db.session.commit()
    flash("Предмет удален", "success")
    return redirect(
        url_for(
            "view_profile", username=current_user.username, weapon_class=weapon_class
        )
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])
    app.run(host="127.0.0.1", port=5000, debug=True)
