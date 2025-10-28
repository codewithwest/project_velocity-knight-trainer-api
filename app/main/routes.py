import os
import datetime
import bcrypt
from flask import render_template, request, redirect, url_for, flash, current_app, session
from . import main
from config import Connection
from werkzeug.utils import secure_filename

@main.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST' and 'login_button' in request.form:
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = Connection.get_db()
        users_collection = db.get_collection('users')
        user = users_collection.find_one({"email": email})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user'] = {'name': user['name'], 'email': user['email'], 'is_admin': user.get('is_admin', False)}
            return redirect(url_for('main.dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'
            
    return render_template('login.html', error=error)

@main.route('/register', methods=['GET', 'POST'])
def register():
    user_session = session.get('user')
    if not user_session or not user_session.get('is_admin'):
        flash('ACCESS_DENIED: REQUIRES_ADMIN_PRIVILEGES.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('PASSWORDS_DO_NOT_MATCH.', 'error')
            return render_template('register.html')

        db = Connection.get_db()
        users_collection = db.get_collection('users')
        
        if users_collection.find_one({"email": email}):
            flash('USER_WITH_EMAIL_EXISTS.', 'error')
            return render_template('register.html')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        users_collection.insert_one({
            "email": email,
            "name": name,
            "password": hashed_password,
            "is_admin": False
        })

        flash('NEW_USER_PROFILE_CREATED_SUCCESSFULLY.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html')


@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # In a real app you would handle password reset email sending here
        flash('A password reset link has been sent to your email.', 'success')
        return redirect(url_for('main.index'))

    return render_template('forgot_password.html')

@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('main.index'))

    db = Connection.get_db()

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file:
            upload_type = request.form.get('upload_type')
            filename = secure_filename(file.filename)
            
            upload_folder = os.path.join(current_app.static_folder, 'uploads', upload_type)
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
            
            db.uploads.insert_one({
                'filename': filename,
                'upload_type': upload_type,
                'user_email': user['email'],
                'user_name': user['name'],
                'upload_date': datetime.datetime.utcnow()
            })
            
            flash(f'File "{filename}" uploaded successfully', 'success')
            return redirect(url_for('main.dashboard'))

    user_email = user['email']
    pdf_files = list(db.uploads.find({'user_email': user_email, 'upload_type': 'pdf'}).sort('upload_date', -1))
    image_.files = list(db.uploads.find({'user_email': user_email, 'upload_type': 'image'}).sort('upload_date', -1))

    uploaded_files = {
        'pdf': pdf_files,
        'image': image_files
    }

    return render_template('dashboard.html', user=user, uploaded_files=uploaded_files)