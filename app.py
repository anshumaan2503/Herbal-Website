from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
from urllib.parse import quote

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')
app.config['DATABASE'] = 'products.db'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Custom Jinja2 filter for URL encoding
@app.template_filter('urlencode')
def urlencode_filter(s):
    return quote(str(s))

# Database helper functions
def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row  # Return rows as dictionaries
    return db

def init_db():
    """Initialize the database"""
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price TEXT NOT NULL,
            image TEXT NOT NULL
        )
    ''')
    db.commit()
    db.close()
    print("✅ SQLite database initialized successfully!")

# Initialize database on startup
init_db()

# ✅ Home page - Show all products
@app.route('/')
def home():
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    db.close()
    return render_template('index.html', products=products)

# Admin login page
@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Simple hardcoded admin credentials
        if username == 'admin' and password == '123':
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

# Admin logout
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# Protect dashboard route
@app.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    db.close()
    return render_template('dashboard.html', products=products)

# Protect add-product route
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.files['image']

        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)

            # Insert product into SQLite
            db = get_db()
            db.execute(
                'INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)',
                (name, description, price, image_filename)
            )
            db.commit()
            db.close()
            flash('Product added successfully!', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_product.html')

# Protect delete route
@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        db = get_db()
        # Fetch product to get image filename
        product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        
        if product:
            # Delete from database
            db.execute('DELETE FROM products WHERE id = ?', (product_id,))
            db.commit()
            
            # Delete image file from disk
            if product['image']:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image'])
                if os.path.exists(image_path):
                    os.remove(image_path)
        
        db.close()
        flash('Product deleted successfully!', 'success')
        
    except Exception as e:
        print(f"Error deleting product: {e}")
        flash('Error deleting product. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

# Change /admin to redirect to login
@app.route('/admin')
def admin():
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
