
from flask import Flask, render_template, url_for, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from db import db
from tables import *
from bcrypt import hashpw, gensalt, checkpw



def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe.db'
    app.secret_key = 'not_so_secret_key'
    db.init_app(app)

    return app

def configure_routes(app):
    @app.route('/', methods = ['POST', 'GET'])
    def index():
        if request.method == "POST":
            source = request.form.get('source')
            if source == "Order or Sign Out":
                print("ORder or Sign out")
                action = request.form.get('action')
                if action == "Sign Out":
                    session['emp'] = None
                    return render_template("index.html", employee=session['emp'])
                elif action == "Start An Order":
                    items = Item.query.order_by(Item.id).all()
                    items_map = {item.id: item for item in items}
                    return render_template("items.html", items=items, items_map=items_map)
                
            elif source == "Return from Cart":
                items = Item.query.order_by(Item.id).all()
                items_map = {item.id: item for item in items}
                Cart.query.delete()
                db.session.commit()
                return render_template('items.html', items=items, items_map=items_map)
            
            else:
                print("Error Undefined Source")
                return render_template("index.html", employee=session['emp'])
        else:
            if 'emp' not in session:
                session['emp'] = None
            return render_template('index.html', employee=session['emp'])
        
    @app.route("/emp", methods=["POST"])
    def employee_setup():
        action = request.form.get("action")
        return render_template('employee.html', action=action)
    
    @app.route("/new_emp",  methods=["POST"])
    def add_new_emp():
        username= request.form.get('username')
        position= request.form.get('position')
        pwd = hashpw(request.form.get('password').encode('utf-8'), gensalt())
        new_emp = Employee(name=username, position=position, password=pwd)
        db.session.add(new_emp)
        db.session.commit()
        return render_template("index.html", employee=session['emp'])

    @app.route('/submit_login', methods=["POST"]) #from js: check_credentials
    def check_login():
        data = request.get_json()
        username = data.get("username")
        user = Employee.query.filter_by(name=username).first()

        if not user or not checkpw(data.get("password").encode('utf-8'), user.password):
            return jsonify({"success": False})
        else:
            session['emp'] = user.id
            return jsonify({"success": True, "redirect": "/"})

        
        
    @app.route('/select_item', methods=["POST"])
    def select_item():
        data = request.get_json()
        item_id = data.get("id")
        item = Item.query.get(item_id)
        if item:
            return jsonify({"success": True, "item_name": item.name})
        return jsonify({"success": False, "message": "Item not found"})
    
    @app.route("/add_item", methods=["POST"])
    def add_item():
        data = request.get_json()
        quantity = data.get("quantity")
        item_id = data.get("id")
        
        cart_item = Cart.query.filter_by(item_id=item_id).first()

        if cart_item:
            cart_item.quantity += int(quantity)
        else:
            new_cart_item = Cart(user_id=1, item_id=item_id, quantity=quantity)
            db.session.add(new_cart_item)

        # Commit the changes to the database
        db.session.commit()
        
        items = Item.query.order_by(Item.id).all()
        items_map = {item.id: item for item in items}

        cart = Cart.query.all()
        cart_html = render_template("cart.html", cart={item.id: item.quantity for item in cart}, items_map=items_map)
        return {'cart_html': cart_html, "item_id": item_id, "item_name": items_map[item_id].name}
        

    @app.route("/clear_session", methods=["POST"])
    def clear_session():
        print("Ran Clear")
        action = request.form.get("action")
        Cart.query.delete()
        db.session.commit()

        if action == "Return to Main Menu":
            return render_template("index.html", employee=session['emp'])
        else: # Just Clear Cart
            items = Item.query.order_by(Item.id).all()
            items_map = {item.id: item for item in items}
            return render_template('items.html', items=items, items_map=items_map)
        
    @app.route("/submit_order", methods=["POST"])
    def submit_order():
        cart_items = Cart.query.all()

        items = Item.query.order_by(Item.id).all()
        items_map = {item.id: item for item in items}

        curr_order = {}
        total_price = total_quantity = 0
        for cart_item in cart_items:
            curr_order[cart_item.item_id] = cart_item.quantity
            total_quantity += cart_item.quantity
            total_price += items_map[int(cart_item.item_id)].price

        new_order = Order(quantity=total_quantity, total_price=total_price, emp_id=session['emp'])
        db.session.add(new_order)
        db.session.commit()
        order_id = new_order.order_id

        for cart_item in cart_items:
            orderitem = OrderItem(order_id=order_id, item_id=cart_item.item_id, quantity=cart_item.quantity)
            db.session.add(orderitem)
        db.session.commit()
        
        return render_template('index.html', employee=session['emp'])
    

if __name__ == "__main__":
    app = create_app()
    configure_routes(app)
    app.run(debug=True)
