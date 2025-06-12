from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Модели User и InventoryItem из предыдущего примера

def init_db():
    with app.app_context():
        db.create_all()
        print("База данных создана!")
        print(f"Путь к БД: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"SECRET_KEY: {app.config['SECRET_KEY']}")

if __name__ == '__main__':
    init_db()
