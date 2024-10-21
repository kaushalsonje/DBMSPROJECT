from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import secrets

secret_key = secrets.token_hex(16)  # Generates a 32-character (16 bytes) hex key

app = Flask(__name__)
app.secret_key = secret_key

# Database configuration
db_config = {
    'user': 'root',
    'password': '111307',  # Replace with your MySQL password
    'host': 'localhost',
    'database': 'medical_shop_db'
}

# Function to get a database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Route to display all medicines
@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # cursor.execute('SELECT * FROM medicines')
    # medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('home.html', medicines=medicines)

@app.route('/medicines')
def list_medicines():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM medicines')
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('list_medicines.html', medicines=medicines)

# Route to add a new medicine
@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        available = quantity > 0

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO medicines (name, price, quantity, available) VALUES (%s, %s, %s, %s)',
                       (name, price, quantity, available))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Medicine added successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_medicine.html')

# Route to record a sale
@app.route('/sell_medicine', methods=['GET', 'POST'])
def sell_medicine():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        medicine_id = int(request.form['medicine_id'])
        customer_name = request.form['customer_name']
        quantity_sold = int(request.form['quantity_sold'])
        sale_price = float(request.form['sale_price'])
        date_sold = request.form['date_sold']

        cursor.execute('SELECT * FROM medicines WHERE id = %s', (medicine_id,))
        medicine = cursor.fetchone()

        if medicine and medicine['quantity'] >= quantity_sold:
            cursor.execute('INSERT INTO sales (medicine_id, customer_name, quantity_sold, sale_price, date_sold) VALUES (%s, %s, %s, %s, %s)',
                           (medicine_id, customer_name, quantity_sold, sale_price, date_sold))

            new_quantity = medicine['quantity'] - quantity_sold
            cursor.execute('UPDATE medicines SET quantity = %s, available = %s WHERE id = %s',
                           (new_quantity, new_quantity > 0, medicine_id))

            conn.commit()
            flash('Medicine sold successfully!')
        else:
            flash('Not enough stock available.')

        cursor.close()
        conn.close()
        return redirect(url_for('list_medicines'))

    cursor.execute('SELECT * FROM medicines')
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('sell_medicine.html', medicines=medicines)

# Route to handle returns
@app.route('/return_medicine', methods=['GET', 'POST'])
def return_medicine():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        sale_id = int(request.form['sale_id'])
        quantity_returned = int(request.form['quantity_returned'])
        return_price = float(request.form['return_price'])
        date_returned = request.form['date_returned']

        cursor.execute('SELECT * FROM sales WHERE id = %s', (sale_id,))
        sale = cursor.fetchone()

        if sale:
            medicine_id = sale['medicine_id']
            customer_name = sale['customer_name']
            cursor.execute('INSERT INTO returns (sale_id, medicine_id, customer_name, quantity_returned, return_price, date_returned) VALUES (%s, %s, %s, %s, %s, %s)',
                           (sale_id, medicine_id, customer_name, quantity_returned, return_price, date_returned))

            cursor.execute('SELECT * FROM medicines WHERE id = %s', (medicine_id,))
            medicine = cursor.fetchone()

            new_quantity = medicine['quantity'] + quantity_returned
            cursor.execute('UPDATE medicines SET quantity = %s, available = %s WHERE id = %s',
                           (new_quantity, new_quantity > 0, medicine_id))

            conn.commit()
            flash('Return processed successfully!')
        else:
            flash('Invalid sale ID.')

        cursor.close()
        conn.close()
        return redirect(url_for('list_medicines'))

    cursor.execute('SELECT * FROM sales')
    sales = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('return_medicine.html', sales=sales)

if __name__ == '__main__':
    app.run(debug=True)
