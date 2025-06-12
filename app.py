import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = '2079acc5744b8f1fe9b9c84cb9a7a21ed531bbca08574b035a2bf52f4bf6cbe7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
# Создаем папку для загрузок, если ее нет
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    items = db.relationship('InventoryItem', backref='user', lazy=True, cascade="all, delete-orphan")

# Модель предмета инвентаря
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # head, torso, gloves, pants
    image_path = db.Column(db.String(255))
    description = db.Column(db.Text)
    pros = db.Column(db.Text)
    cons = db.Column(db.Text)
    rating = db.Column(db.Integer)

# Создаем таблицы в БД
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Главная страница (вход/регистрация)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if 'register' in request.form:
            # Регистрация нового пользователя
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Пользователь с таким именем уже существует', 'error')
                return redirect(url_for('index'))
            
            hashed_password = generate_password_hash(password,method='pbkdf2:sha256') 
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('index'))
        
        elif 'login' in request.form:
            # Вход существующего пользователя
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect(url_for('profile'))
            else:
                flash('Неверное имя пользователя или пароль', 'error')
                return redirect(url_for('index'))
    
    return render_template('index.html')

# Личный кабинет с инвентарем
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    items = InventoryItem.query.filter_by(user_id=user_id).all()
    
    # Группируем предметы по типам для удобного отображения
    inventory = {
        'head': next((item for item in items if item.item_type == 'head'), None),
        'torso': next((item for item in items if item.item_type == 'torso'), None),
        'gloves': next((item for item in items if item.item_type == 'gloves'), None),
        'pants': next((item for item in items if item.item_type == 'pants'), None)
    }
    
    return render_template('profile.html', inventory=inventory, username=session['username'])

# Загрузка изображения и информации о предмете
@app.route('/upload/<item_type>', methods=['GET', 'POST'])
def upload(item_type):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Обработка загрузки файла
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{session['user_id']}_{item_type}.{file.filename.rsplit('.', 1)[1].lower()}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Создаем или обновляем запись в БД
            item = InventoryItem.query.filter_by(user_id=session['user_id'], item_type=item_type).first()
            if not item:
                item = InventoryItem(
                    user_id=session['user_id'],
                    item_type=item_type,
                    image_path=filename,
                    description=request.form['description'],
                    pros=request.form['pros'],
                    cons=request.form['cons'],
                    rating=int(request.form['rating'])
                )
                db.session.add(item)
            else:
                item.image_path = filename
                item.description = request.form['description']
                item.pros = request.form['pros']
                item.cons = request.form['cons']
                item.rating = int(request.form['rating'])
            
            db.session.commit()
            flash('Предмет успешно сохранен!', 'success')
            return redirect(url_for('profile'))
    
    return render_template('upload.html', item_type=item_type)

# Выход из системы
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/delete/<item_type>', methods=['POST'])
def delete_item(item_type):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    # Находим предмет в базе данных
    item = InventoryItem.query.filter_by(
        user_id=session['user_id'],
        item_type=item_type
    ).first()
    
    if item:
        try:
            # Удаляем файл изображения
            if item.image_path:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], item.image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Удаляем запись из БД
            db.session.delete(item)
            db.session.commit()
            flash('Предмет успешно удален', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при удалении: {str(e)}', 'error')
    
    return redirect(url_for('profile'))

@app.route('/edit/<item_type>', methods=['GET', 'POST'])
def edit_item(item_type):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    item = InventoryItem.query.filter_by(
        user_id=session['user_id'],
        item_type=item_type
    ).first_or_404()
    
    if request.method == 'POST':
        # Обработка загрузки нового изображения
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            # Удаляем старое изображение
            if item.image_path:
                old_file = os.path.join(app.config['UPLOAD_FOLDER'], item.image_path)
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            # Сохраняем новое изображение
            filename = secure_filename(f"{session['user_id']}_{item_type}.{file.filename.rsplit('.', 1)[1].lower()}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            item.image_path = filename
        
        # Обновляем информацию
        item.description = request.form['description']
        item.pros = request.form['pros']
        item.cons = request.form['cons']
        item.rating = int(request.form['rating'])
        
        db.session.commit()
        flash('Изменения сохранены!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit.html', item=item, item_type=item_type)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
