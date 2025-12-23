from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# This Initializes the database's connection and is what I'll use for my database stuff

class Product(db.Model):
    id = db.Column(db.Integer,
    primary_key=True)
    # This is the main ID for each product, so each one is unique.

    name = db.Column(db.String(100),
    unique=True, nullable=False)
    # I made it unique=True so no two products have the same name.
    # nullable=False means it must have a name.

    description = db.Column(db.Text,
    nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100))
    carbon_footprint = db.Column(db.Float)
    def __repr__(self):
        return f'<Product {self.name}>'
        # This just helps me when I'm debugging. If I print a Product, it shows its name.
# This class defines what details each product will have stored in the database.
# The variuos clases also sets different rules to follow for description, price and image


class Cart(db.Model):
    id = db.Column(db.Integer,
    primary_key=True)
    # Each item ever added to any cart gets its own unique ID here. It's the primary key for this table.

    session_id = db.Column(db.String(100),
    nullable=False, index=True)
    # This links the cart item to a specific user's Browse session.

    product_id = db.Column(db.Integer,
    db.ForeignKey('product.id'), nullable=False)
    # This connects this cart entry to an actual product in the Product table.
    # The db.ForeignKey part makes sure it matches a real product ID. Can't be empty.

    quantity = db.Column(db.Integer, default=1)
    # How many of this specific product the user wants. Defaults to 1 when they first add something.

    product = db.relationship('Product', backref=db.backref('cart_associations', lazy=True))
    # The 'backref' part adds 'cart_associations' to the Product model, so I could
    # find all cart entries for a specific product if I needed (though I didn't use it much).

    def __repr__(self):
        # Like with Product, this is for debugging, so I can print a Cart item and see what it is.
        return f'<CartItem product_id={self.product_id} quantity={self.quantity} session={self.session_id}>'
    # It tracks what a user wants to buy since users aren't logged in with accounts
    # I continued the compact code tyle by using multiples lines to shorten code