
# These are the imports i need from libaries and flask

from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify, flash
from models import db, Product, Cart 
import uuid
from werkzeug.exceptions import HTTPException
from datetime import timedelta
import os


# ---Application Setup---

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_very_secret_dev_key_123!@#_v4')
# Initializing the flask application and setting up the secret key config for security

app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///shop.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'PERMANENT_SESSION_LIFETIME': timedelta(days=1)
})
# Telling the Flask-SQLAlchemy where the database file is
# I also decided to disable the modification tracking since it saves memory and not needed

db.init_app(app)


# - I decided to group the non-route functions together to improve structure


def init_products():
    """Populates the database with sample products if it's empty."""
    with app.app_context(): 
        if not Product.query.first():
            products_data = [
                {
                    "name": "Air Jordan 1 Retro High OG",
                    "description": "The Jordan 1 is a classic shoe that brings a iconic Nike swoosh, Jordan wings logo and a comfortable Air-sole unit. We bring you a unique Brown and Black Retro High OG colourway that gives a more casual formal look. The Jordan 1 is also crafted with a premium leather upper for durability and is the most famous Jordan shoe due to being famously worn by Michael Jordan himself during his rookie season, which changed the future of sneakers for decades to come.",
                    "price": 180.00,
                    "image": "Jordan1.jpg",
                    "carbon_footprint": 12.5
                },
                {
                    "name": "Jordan 4 Retro 'Bred Reimagined'",
                    "description": "The Jordan 4 is a fan favourite shoe that brings a mesh netting, distinctive wings and a visible Air-sole and the retro 'bred' is an iconic silhouette, which was released in 1989 and had a surge of popularity cementing itself in being one of the most popular Jordan 4 colourway. Welcome the new Jordan 4 retro 'Bred Reimagined', It's a new shoe that bring back that iconic colourway with a new premium full-grain leather that brings a new modern and luxury feel to the Jordan classic.",
                    "price": 220.00,
                    "image": "Jordan4.jpg",
                    "carbon_footprint": 14.0
                },
                {
                    "name": "Jordan 11 Retro 'Concord'",
                    "description": "The Jordan 11 is a Elegant shoe that meets peak performance as it's a iconic  Jordan shoe due to being debuted by Michael Jordan during his dominant 96-96 NBA championship season, which just shoes how much of a masterpiece this shoe is. The Jordan 11's aren't only amazing for performance and quality but the iconic 'Concord' design is a beautiful colourway with a mix of black and white, these reasons mixed with the carbon fiber spring plate and luxury on and off court design leads many sources to cite this shoe as the greatest sneaker of all time.",
                    "price": 225.00,
                    "image": "Jordan11.jpg",
                    "carbon_footprint": 15.2
                },
                {
                    "name": "Jordan 3 Retro 'White Cement'",
                    "description": "The Jordan 3 Retro 'White Cement' has a breath-taking design created by the legendary Tinker Hatfield. The shoes was a game-changer that had met both criteria of comfort and style whilst completely revolutionizing sneaker culture around the world. It has become one of the most highly recognised Jordan shoes with its white tumbled leather upper and the iconic elephant print overlays on the toe and mudguard, which has become a design intertwined with Jordan shoes.",
                    "price": 200.00,
                    "image": "Jordan3.jpg",
                    "carbon_footprint": 13.8
                }
                # defining sample product data
            ]
            for product_data in products_data:
                existing_product = Product.query.filter_by(name=product_data["name"]).first()
                if not existing_product:
                    product = Product(**product_data)
                    db.session.add(product)
            db.session.commit()
            app.logger.info(" I've Initialized sample products with more detailed descriptions! (if any were new)")
            # Gave the log confirmation some personality because why not
            # Use this to add new products to the database session and commits them to the database

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        app.logger.info(f"New session created: {session['session_id']}")
    return session['session_id']
# I used this to check if th esession_id is in the users cookie and if it isn't then it generates a new ID and stores it
# Then it logs and return the session ID wheather its the esisting or newly created one

def create_db():
    with app.app_context(): db.create_all(); init_products()
# I used this function to create database tables if they dont exist and initialises products
# It creates the tables from the models in models.py


# --- This is where the Routes starts so it's structures in the middle and main part of the code


# --- Routes ---


@app.route('/')
def home():
    sorting_by = request.args.get('sort', 'name')

    if sorting_by == 'price':
        products = Product.query.order_by(Product.price.desc()).all()
        # It Sorts by price DESCENDING (highest first)
    elif sorting_by == 'carbon':
        products = Product.query.order_by(Product.carbon_footprint.desc()).all()
        #  I used the same method to Sort the carbon footprint
    else:
        products = Product.query.order_by(Product.name.asc()).all()

    return render_template('index.html', products=products, current_sort=sorting_by)
# Making sure to render the index template pass the sorted and current criteria
# This is the main route for the hompage and product listing


@app.route('/product/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    get_session_id()
    # It gets the product by it ID and ensures that a session ID definity ecxists for the user to stop problems occuring
    # I also made it so it return 404 if one isnt found

    if 'recently_viewed' not in session: session['recently_viewed'] = []
    session['recently_viewed'] = [pid for pid in session['recently_viewed'] if pid != product_id]
    session['recently_viewed'].insert(0, product_id)
    session['recently_viewed'] = session['recently_viewed'][:4]
    recently_viewed_ids = [pid for pid in session['recently_viewed'] if pid != product_id][:3]
    recently_viewed_products = []
    if recently_viewed_ids:
        recently_viewed_products = Product.query.filter(Product.id.in_(recently_viewed_ids)).all()
        if recently_viewed_products: recently_viewed_products.sort(key=lambda x: recently_viewed_ids.index(x.id))
    session.modified = True
    return render_template('products.html', product=product, recently_viewed=recently_viewed_products)
# The products_details function displays the detail pages and updates recently viewed items
# I had alot of issues when trying to implement the recently viewed items and finaly found it to work well in this function


# --- I made sure to group all the cart functions together and made it so it folows the steps a buyer would have when buying a product,
# --- so adding to car, viewing cart, updating the cart details, removing stuff from cart and finally checkout

 
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'error', 'message': 'Invalid request type.'}), 403
    current_session_id = get_session_id()
    product = Product.query.get_or_404(product_id)
    # I made it so it expects AJAX request to enhance the securitly a little

    try:
        cart_item = Cart.query.filter_by(session_id=current_session_id,
        product_id=product_id).first()
        message = ""
        if cart_item:
            cart_item.quantity += 1; message = f"'{product.name}' quantity updated."
        else:
            cart_item = Cart(session_id=current_session_id, product_id=product_id, quantity=1)
            db.session.add(cart_item); message = f"'{product.name}' added to cart."
        db.session.commit()
        return jsonify({'status': 'success', 'message': message,
        'quantity': cart_item.quantity, 'product_name': product.name})
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Add to cart error: {e}")
        return jsonify({'status': 'error', 'message': 'Server error adding item.'}), 500
# It ads a product to the cart and can increment its quantity


@app.route('/cart')
def view_cart():
    current_session_id = get_session_id()
    cart_items_detailed = db.session.query(Cart, Product)\
    .join(Product, Cart.product_id == Product.id)\
    .filter(Cart.session_id == current_session_id).all()

    products_in_cart = []
    grand_total, total_carbon_impact = 0.0, 0.0
    for cart_entry, product_info in cart_items_detailed:
        item_total = product_info.price * cart_entry.quantity
        products_in_cart.append({
            'cart_item_id': cart_entry.id, 'product_id': product_info.id, 'name': product_info.name,
            'price': product_info.price, 'quantity': cart_entry.quantity, 'image': product_info.image,
            'carbon_footprint': product_info.carbon_footprint, 'item_total_price': item_total
        })
        grand_total += item_total; total_carbon_impact += product_info.carbon_footprint * cart_entry.quantity
    return render_template('cart.html', items=products_in_cart, grand_total=round(grand_total,2), total_carbon_impact=round(total_carbon_impact,2))
# This function is used to display the cart page


@app.route('/update_cart_item/<int:cart_item_id>', methods=['POST'])
def update_cart_item(cart_item_id):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest': return jsonify({'status':'error', 'message':'Invalid request.'}), 403
    cs_id = get_session_id()
    action = request.json.get('action')
    item = Cart.query.filter_by(id=cart_item_id, session_id=cs_id).first_or_404()
    # It gets the incr or decr fromthe JSOn payload of the request and finds the specific item by its ID and user session
    # I also made it return 404 if its not found
    try:
        if action == 'increase': item.quantity +=1
        elif action == 'decrease':
            item.quantity -=1
            if item.quantity <=0:
                db.session.delete(item); db.session.commit()
                return jsonify({'status':'removed',
                'message':'Item removed.'})
        db.session.commit()
        prod = Product.query.get(item.product_id)
        return jsonify({'status':'success',
        'new_quantity':item.quantity,
        'item_total_price': prod.price * item.quantity, 'message':'Cart updated.'})
    except Exception as e:
        db.session.rollback(); app.logger.error(f"Update cart error: {e}")
        return jsonify({'status':'error',
         'message':'Could not update item.'}), 500
# I made this function increase or decrease the items in the cart
# I made sure to create i more compact designed code by spliting lists into multiples lines throughout the code


@app.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    cs_id = get_session_id()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    app.logger.info(f"Remove attempt: cart_item_id={cart_item_id}, session={cs_id}, AJAX={is_ajax}")
    # Checks if request is likely AJAX
    try:
        item = Cart.query.filter_by(id=cart_item_id, session_id=cs_id).first()
        if item:
            prod_name = item.product.name if item.product else "Item"
            db.session.delete(item); db.session.commit()
            app.logger.info(f"Removed CartItem ID {cart_item_id} for session {cs_id}")
            if not is_ajax: flash(f"'{prod_name}' removed.", 'success')
            if is_ajax: return jsonify({'status':'success',
            'message':f"'{prod_name}' removed."})
            # Gets and deletes the item from database sesion
        else:
            app.logger.warning(f"CartItem ID {cart_item_id} not found for session {cs_id} on remove.")
            if not is_ajax: flash('Item not found in cart.', 'warning')
            if is_ajax: return jsonify({'status':'error',
            'message':'Item not found.'}), 404
            # If item wasnt found then returns responses for AJAX and non-AJAX

    except Exception as e:
        db.session.rollback(); app.logger.error(f"Remove cart error: {e}")
        if not is_ajax: flash('Error removing item.', 'error')
        if is_ajax: return jsonify({'status':'error',
        'message':'Server error removing item.'}), 500
    return redirect(url_for('view_cart'))
# Removes an item entirely from the cart which had casued alot of bugs when making so its alot more code then i had hoped to make it


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cs_id = get_session_id()
    cart_items = db.session.query(Cart,Product).join(Product,
    Cart.product_id==Product.id).filter(Cart.session_id==cs_id).all()
    if not cart_items and request.method == 'GET':
        flash('Cart is empty.', 'info')
        return redirect(url_for('view_cart'))
    # It displays items in cart and checks if cart is empty
    # I made sure it did these intructions right after each other so if someones removes a product on GET request,
    # it redirect them back to the page so it happens fast
    
    total = sum(p.price*c.quantity for c,p in cart_items)
    carbon = sum(p.carbon_footprint*c.quantity for c,p in cart_items)
    # The mathsy bit for the displays on both the GET and POST

    if request.method == 'POST':
        errors, data = {}, request.form
        card_num = data.get('card_number','').replace(' ','').replace('-','')
        if not (card_num.isdigit() and len(card_num)==16): errors['card_number'] = 'Valid 16-digit card required.'
        for f,n in {'card_name':'Name on card','expiry':'Expiry MM/YY','cvv':'CVV'}.items():
            if not data.get(f): errors[f] = f'{n} is required.'
        if errors:
            flash('Correct form errors.', 'danger')
            return render_template('checkout.html',errors=errors,form_data=data,grand_total=round(total,2),total_carbon_impact=round(carbon,2))
        Cart.query.filter_by(session_id=cs_id).delete(); db.session.commit()
        flash('Checkout successful!', 'success')
        return render_template('checkout_success.html',grand_total=round(total,2),total_carbon_impact=round(carbon,2))
    return render_template('checkout.html',errors={},form_data={},grand_total=round(total,2),total_carbon_impact=round(carbon,2))
    # Handles the form submission and does validation checks
# Displays the checkout form (GET)
# Processes payment detail (POST)


@app.route('/search')
def search():
    queries = request.args.get('q','').strip()
    if not queries: return redirect(url_for('home'))
    # It rediracts home if query is empty which is a good base as its automatically empty

    term = f"%{queries}%"
    prods = Product.query.filter(Product.name.ilike(term)|Product.description.ilike(term)).all()

    flash(f"{len(prods)} product(s) found for '{queries}'.", 'info' if prods else 'warning')
    return render_template('index.html',products=prods,search_query=queries,current_sort='search')
# Performs a search for products based on query parameters which makes it case-insensitive


@app.route('/product/<int:product_id>/details_ajax')
def product_details_ajax(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify({'id':p.id,'name':p.name,
    'description':p.description,'price':p.price,
    'image':url_for('static',filename=f'images/{p.image}'),
    'carbon_footprint':p.carbon_footprint})
# Makes sure to return th eproduct details in JSON format for the AJAX requests



# --- Error Handlers ---


# --- I made sure to leave the error handling to last just to keep it hidden at the bottom of the code in it own section as a stylic choice


@app.errorhandler(404)
def err_404(e): return render_template('404.html',error=e),404
@app.errorhandler(500)
def err_500(e): db.session.rollback(); app.logger.error(f"500 Error: {e}"); return render_template('500.html',error=e),500
@app.errorhandler(HTTPException)
def http_err(e): app.logger.warning(f"HTTP Err: {e.code} {e.name}"); return render_template('error_generic.html',error=e),e.code

# --- Main ---

if __name__ == '__main__':
    create_db()
    app.run(debug=True)