from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import os
from werkzeug.utils import secure_filename
from bson import ObjectId
from urllib.parse import quote

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Use environment variable

# MongoDB Configuration
MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = os.environ.get('DB_NAME', "herbaluser")
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', "herbaluser")

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    # Test the connection
    client.admin.command('ping')
    db = client[DB_NAME]
    products_collection = db[COLLECTION_NAME]
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("Please make sure MongoDB is running on localhost:27017")
    client = None
    db = None
    products_collection = None

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Custom Jinja2 filter for URL encoding
@app.template_filter('urlencode')
def urlencode_filter(s):
    return quote(str(s))

def init_db():
    if products_collection is not None:
        # Create indexes for better performance
        products_collection.create_index("name")
        print("MongoDB database initialized successfully!")
    else:
        print("❌ Cannot initialize database - MongoDB not connected")

init_db()

# ✅ Home page - Show all products
@app.route('/')
def home():
    if products_collection is not None:
        products = list(products_collection.find())
    else:
        products = []
        flash('Database connection error. Please try again later.', 'error')
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
    if products_collection is not None:
        products = list(products_collection.find())
    else:
        products = []
        flash('Database connection error. Please try again later.', 'error')
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

            # Insert product into MongoDB
            if products_collection is not None:
                product_data = {
                    'name': name,
                    'description': description,
                    'price': price,
                    'image': image_filename
                }
                products_collection.insert_one(product_data)
                flash('Product added successfully!', 'success')
            else:
                flash('Database connection error. Product not saved.', 'error')

        return redirect(url_for('dashboard'))

    return render_template('add_product.html')

# Protect delete route
@app.route('/delete/<product_id>')
def delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        if products_collection is not None:
            # Convert string ID to ObjectId
            product_object_id = ObjectId(product_id)
            
            # Fetch image filename before deletion
            product = products_collection.find_one({'_id': product_object_id})
            
            if product:
                # Delete from database
                products_collection.delete_one({'_id': product_object_id})
                
                # Delete image file from disk
                if product.get('image'):
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image'])
                    if os.path.exists(image_path):
                        os.remove(image_path)
        else:
            flash('Database connection error. Product not deleted.', 'error')
        
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
