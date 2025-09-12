import os
import datetime
from flask import render_template, request, redirect, url_for, flash, current_app, session
from . import main
from app import mongo
from werkzeug.utils import secure_filename

@main.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Mock authentication
        if email and password:
            # In a real app, you'd verify the credentials here
            session['user'] = {'name': email.split('@')[0], 'email': email}
            return redirect(url_for('main.dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'
            
    return render_template('login.html', error=error)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password == confirm_password:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Passwords do not match.', 'error')

    return render_template('register.html')

@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        flash('A password reset link has been sent to your email.', 'success')
        return redirect(url_for('main.index'))

    return render_template('forgot_password.html')

@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('main.index'))

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
            
            mongo.db.uploads.insert_one({
                'filename': filename,
                'upload_type': upload_type,
                'user_email': user['email'],
                'user_name': user['name'],
                'upload_date': datetime.datetime.utcnow()
            })
            
            flash(f'File "{filename}" uploaded successfully', 'success')
            return redirect(url_for('main.dashboard'))

    user_email = user['email']
    pdf_files = list(mongo.db.uploads.find({'user_email': user_email, 'upload_type': 'pdf'}).sort('upload_date', -1))
    image_files = list(mongo.db.uploads.find({'user_email': user_email, 'upload_type': 'image'}).sort('upload_date', -1))

    uploaded_files = {
        'pdf': pdf_files,
        'image': image_files
    }

    return render_template('dashboard.html', user=user, uploaded_files=uploaded_files)
