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
import hashlib
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# MongoDB Connection
MONGO_URI = os.environ.get('MONGO_URI', "mongodb+srv://admin:Ans%23umaan2003@cluster0.jssosyw.mongodb.net/herbal_website?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database('herbal_website')

products_collection = db.products
users_collection    = db.users
reviews_collection  = db.reviews

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
    def get_image_url(image_path, width=None):
        if not image_path:
            # Fallback with optional width
            transformation = f"f_auto,q_auto{',w_' + str(width) + ',c_scale' if width else ''}"
            return f"https://res.cloudinary.com/demo/image/upload/{transformation}/sample.jpg"
        
        if image_path.startswith('http'):
            # If it's a Cloudinary URL, inject auto-optimization and resizing
            if 'cloudinary.com' in image_path and '/upload/' in image_path:
                transformation = f"f_auto,q_auto{',w_' + str(width) + ',c_scale' if width else ''}"
                return image_path.replace('/upload/', f'/upload/{transformation}/')
            return image_path
            
        # If it's a local path, try to serve it
        return url_for('static', filename='images/' + image_path)
    return dict(get_image_url=get_image_url)

# ✅ Home page - Show all products
@app.route('/')
def home():
    try:
        products = list(products_collection.find())
        # Group reviews by product_id for template use
        all_reviews = list(reviews_collection.find())
        reviews_by_product = {}
        for r in all_reviews:
            pid = r['product_id']
            reviews_by_product.setdefault(pid, []).append(r)
        return render_template('index.html', products=products, reviews_by_product=reviews_by_product)
    except Exception as e:
        return f"Database error: {e}"

# Config check route for debugging
@app.route('/check_config')
def check_config():
    if not session.get('admin_logged_in'):
        return "Please login as admin first to see config."
    config_status = {
        "Cloud Name": os.environ.get('CLOUDINARY_CLOUD_NAME', '❌ NOT SET'),
        "API Key": "✅ SET" if os.environ.get('CLOUDINARY_API_KEY') else "❌ NOT SET",
        "API Secret": "✅ SET" if os.environ.get('CLOUDINARY_API_SECRET') else "❌ NOT SET",
        "MongoDB URI": "✅ SET" if os.environ.get('MONGO_URI') else "❌ NOT SET (Using Code Fallback)",
    }
    return f"<h3>System Configuration Check</h3><pre>{config_status}</pre><a href='/dashboard'>Back to Dashboard</a>"

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
                # Fallback to local storage if Cloudinary fails
                flash(f'Cloudinary Error: {e}. Image saved locally (non-persistent).', 'danger')
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

@app.route('/edit/<string:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if not product:
        flash('Product not found!', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.files.get('image')

        update_data = {
            'name': name,
            'description': description,
            'price': price
        }

        if image and image.filename != '':
            try:
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(image)
                update_data['image'] = upload_result['secure_url']
            except Exception as e:
                print(f"Cloudinary upload failed: {e}")
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)
                update_data['image'] = image_filename

        products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': update_data})
        flash('Product updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_product.html', product=product)

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


# ─── User Registration ────────────────────────────────────────────────────────

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route('/register', methods=['GET', 'POST'])
def user_register():
    if session.get('user_logged_in'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('user_register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('user_register.html')

        if users_collection.find_one({'email': email}):
            flash('An account with this email already exists.', 'danger')
            return render_template('user_register.html')

        users_collection.insert_one({
            'name'    : name,
            'email'   : email,
            'password': hash_password(password),
            'created' : datetime.utcnow()
        })
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('user_login'))

    return render_template('user_register.html')


@app.route('/user-login', methods=['GET', 'POST'])
def user_login():
    if session.get('user_logged_in'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = users_collection.find_one({'email': email, 'password': hash_password(password)})
        if user:
            session['user_logged_in'] = True
            session['user_name']      = user['name']
            session['user_id']        = str(user['_id'])
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('user_login.html')


@app.route('/user-logout')
def user_logout():
    session.pop('user_logged_in', None)
    session.pop('user_name', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


# ─── Reviews ──────────────────────────────────────────────────────────────────

@app.route('/review/<string:product_id>', methods=['POST'])
def submit_review(product_id):
    if not session.get('user_logged_in'):
        flash('Please log in to submit a review.', 'danger')
        return redirect(url_for('user_login'))

    rating  = request.form.get('rating', '5')
    comment = request.form.get('comment', '').strip()

    if not comment:
        flash('Review comment cannot be empty.', 'danger')
        return redirect(url_for('home') + f'#product-{product_id}')

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            rating = 5
    except ValueError:
        rating = 5

    # Check if user already reviewed this product
    existing = reviews_collection.find_one({
        'product_id': product_id,
        'user_id'   : session['user_id']
    })
    if existing:
        flash('You have already reviewed this product.', 'danger')
        return redirect(url_for('home') + f'#product-{product_id}')

    reviews_collection.insert_one({
        'product_id': product_id,
        'user_id'   : session['user_id'],
        'user_name' : session['user_name'],
        'rating'    : rating,
        'comment'   : comment,
        'date'      : datetime.utcnow()
    })
    flash('Thank you for your review!', 'success')
    return redirect(url_for('home') + f'#rmodal-{product_id}')


@app.route('/review/delete/<string:review_id>', methods=['POST'])
def delete_review(review_id):
    if not session.get('user_logged_in'):
        flash('Please log in first.', 'danger')
        return redirect(url_for('user_login'))

    try:
        review = reviews_collection.find_one({'_id': ObjectId(review_id)})
        if not review:
            flash('Review not found.', 'danger')
        elif review['user_id'] != session['user_id']:
            flash('You can only delete your own review.', 'danger')
        else:
            reviews_collection.delete_one({'_id': ObjectId(review_id)})
            flash('Your review has been deleted.', 'success')
    except Exception as e:
        flash('Error deleting review. Please try again.', 'danger')

    return redirect(url_for('home'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

