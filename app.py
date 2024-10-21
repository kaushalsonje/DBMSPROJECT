from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import os
import secrets

secret_key = secrets.token_hex(16)  # Generates a 32-character (16 bytes) hex key


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/medical_shop_db"
app.secret_key = secret_key
mongo = PyMongo(app)

# Route to display all medicines
@app.route('/')
def home():
    medicines = mongo.db.medicines.find()
    return render_template('home.html', medicines=medicines)

@app.route('/medicines')
def list_medicines():
    medicines = mongo.db.medicines.find()
    return render_template('list_medicines.html', medicines=medicines)


# Route to add a new medicine
@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        # Get the data from the form
        try:
            _id = int(request.form['_id'])  # Numeric ID from user input
        except ValueError:
            flash("Please enter a valid numeric ID.")
            # return redirect(url_for('add_medicine'))

        name = request.form['name']
        price = int(request.form['price'])
        quantity = int(request.form['quantity'])

        # Check for a unique numeric id
        existing_medicine = mongo.db.medicines.find_one({"_id": _id})  # Check for existing medicine by _id
        if existing_medicine:
            flash("Medicine with this ID already exists. Please use a different ID.")
            return redirect(url_for('add_medicine'))

        # Create a new medicine record
        medicine = {
            "_id": _id,  # Use the numeric ID
            "name": name,
            "price": price,
            "available": quantity > 0,
            "quantity": quantity
        }

        # Insert into the database
        mongo.db.medicines.insert_one(medicine)
        flash("Medicine added successfully!",'success')
        return redirect(url_for('home'))

    return render_template('add_medicine.html')

# Route to record a sale
@app.route('/sell_medicine', methods=['GET', 'POST'])
def sell_medicine():
    if request.method == 'POST':
        try:
            medicine_id = int(request.form['medicine_id'])
            customer_name = request.form['customer_name']
            quantity_sold = int(request.form['quantity_sold'])
            sale_price = float(request.form['sale_price'])
            date_sold = request.form['date_sold']

            medicine = mongo.db.medicines.find_one({"_id": medicine_id})
            if medicine and medicine['quantity'] >= quantity_sold:
                mongo.db.sales.insert_one({
                    "medicine_id": medicine_id,
                    "customer_name": customer_name,
                    "medicine_name": medicine['name'],
                    "sale_price": sale_price,
                    "quantity_sold": quantity_sold,
                    "date": date_sold
                })

                new_quantity = medicine['quantity'] - quantity_sold
                mongo.db.medicines.update_one(
                    {"_id": medicine_id},
                    {"$set": {"quantity": new_quantity, "available": new_quantity > 0}}
                )

                flash('Medicine sold successfully!')
            else:
                flash('Not enough stock available.')

            return redirect(url_for('list_medicines'))

        except ValueError:
            flash("Invalid input. Please enter valid numeric values.")
            return redirect(url_for('sell_medicine'))

    medicines = mongo.db.medicines.find()
    return render_template('sell_medicine.html', medicines=medicines)

# Route to handle returns
@app.route('/return_medicine', methods=['GET', 'POST'])
def return_medicine():
    if request.method == 'POST':
        try:
            medicine_id = int(request.form['medicine_id'])
            customer_name = request.form['customer_name']
            quantity_sold = int(request.form['quantity_sold'])
            sale_price = float(request.form['sale_price'])
            date_sold = request.form['date_sold']

            medicine = mongo.db.medicines.find_one({"_id": medicine_id})
            mongo.db.sales.insert_one({
                "medicine_id": medicine_id,
                "customer_name": customer_name,
                "medicine_name": medicine['name'],
                "sale_price": sale_price,
                "quantity_sold": quantity_sold,
                "date": date_sold
            })

            new_quantity = medicine['quantity'] + quantity_sold
            mongo.db.medicines.update_one(
                {"_id": medicine_id},
                {"$set": {"quantity": new_quantity, "available": new_quantity > 0}}
            )

            flash('Medicine sold successfully!')
            return redirect(url_for('list_medicines'))

        except ValueError:
            flash("Invalid input. Please enter valid numeric values.")
            return redirect(url_for('sell_medicine'))



    # Fetch medicines for the form
    medicines = mongo.db.medicines.find()
    return render_template('return_medicine.html', medicines=medicines)

if __name__ == '__main__':
    app.run(debug=True)
