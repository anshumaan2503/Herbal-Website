from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
from urllib.parse import quote
from pymongo import MongoClient
from bson.objectid import ObjectId
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import certifi

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# MongoDB Connection
MONGO_URI = os.environ.get('MONGO_URI', "mongodb+srv://admin:Ans%23umaan2003@cluster0.jssosyw.mongodb.net/herbal_website?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database('herbal_website')

products_collection = db.products

# Cloudinary Configuration
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'your_cloud_name'),
    api_key = os.environ.get('CLOUDINARY_API_KEY', 'your_api_key'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', 'your_api_secret'),
    secure = True
)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Custom Jinja2 filter for URL encoding
@app.template_filter('urlencode')
def urlencode_filter(s):
    return quote(str(s))

# Custom helper to get image URL (works for both local and cloudinary)
@app.context_processor
def utility_processor():
    def get_image_url(image_path):
        if not image_path:
            return ""
        if image_path.startswith('http'):
            return image_path
        return url_for('static', filename='images/' + image_path)
    return dict(get_image_url=get_image_url)

# ✅ Home page - Show all products
@app.route('/')
def home():
    products = list(products_collection.find())
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
    products = list(products_collection.find())
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

        image_url = ""
        if image and image.filename != '':
            try:
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(image)
                image_url = upload_result['secure_url']
            except Exception as e:
                # Fallback to local storage if Cloudinary fails/not configured
                print(f"Cloudinary upload failed: {e}")
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)
                image_url = image_filename

            # Insert product into MongoDB
            product_data = {
                'name': name,
                'description': description,
                'price': price,
                'image': image_url
            }
            products_collection.insert_one(product_data)
            flash('Product added successfully!', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_product.html')

# Protect delete route
@app.route('/delete/<string:product_id>')
def delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Fetch product
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        
        if product:
            # Delete from database
            products_collection.delete_one({'_id': ObjectId(product_id)})
            
            # Delete local image if it exists
            image_path_str = product.get('image', '')
            if image_path_str and not image_path_str.startswith('http'):
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path_str)
                if os.path.exists(image_path):
                    os.remove(image_path)
        
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

