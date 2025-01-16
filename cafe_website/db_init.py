from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
from db import db
from app import create_app
from tables import Item, Employee
from bcrypt import hashpw, gensalt, checkpw


def populate_items():
    initial_items = [
        {"name": "Espresso", "category": "Coffee", "size": "Small", "price": 2.50},
        {"name": "Latte", "category": "Coffee", "size": "Medium", "price": 3.50},
        {"name": "Cappuccino", "category": "Coffee", "size": "Large", "price": 4.00},
        {"name": "Green Tea", "category": "Tea", "size": "Small", "price": 2.00},
        {"name": "Black Tea", "category": "Tea", "size": "Medium", "price": 2.50},
        {"name": "Blueberry Muffin", "category": "Snack", "size": None, "price": 2.75},
    ]

    for item in initial_items:
        db.session.add(Item(**item))
    db.session.commit()

def create_general_manager():
    password = hashpw(str(input("Set your Password")).encode("utf-8"), gensalt())
    db.session.add(Employee(id=1, name="Raymond", position="Main Manager", password=password))
    db.session.commit()
# Create the database tables
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        populate_items()
        create_general_manager()

