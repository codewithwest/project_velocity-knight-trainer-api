import os
import datetime
from flask import Flask, request, render_template, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from config import Connection
from uuid import uuid1


app = Flask(__name__, static_folder='app/static',
            template_folder='app/templates/')
app.secret_key = "dtyuiolk vngjiuoipok"
db_connection = Connection()


@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db_connection.get_collection('users').find_one({
            "email": email,
            "password": password
        })

        if user and len(user):
            session.clear()
            flash("Login Successful!, Welcome!")
            session.setdefault('user', {
                "email": email,
                "password": password
            })

            print(session.get('user'))
            return redirect(url_for('dashboard'))
        else:
            flash('Login error, please try again!')

    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password == confirm_password:
            db_connection.get_collection('users').insert_one({
                "email": email, "password": confirm_password})
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Passwords do not match.', 'error')

    return render_template('register.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        flash('A password reset link has been sent to your email.', 'success')
        return redirect(url_for('index'))

    return render_template('forgot_password.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))

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

            upload_folder = os.path.join(
                current_app.static_folder, 'uploads', upload_type)
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))

            db_connection.get_collection('uploads').insert_one({
                'filename': filename,
                'upload_type': upload_type,
                'user_email': user.get('email'),
                # 'user_name': user['name'],
                'upload_date': datetime.datetime.utcnow()
            })

            flash(f'File "{filename}" uploaded successfully', 'success')
            return redirect(url_for('dashboard'))

    user_email = user.get("email")
    pdf_files = list(db_connection.get_collection('uploads').find(
        {'user_email': user_email, 'upload_type': 'pdf'}).sort('upload_date', -1))
    image_files = list(db_connection.get_collection('uploads').find(
        {'user_email': user_email, 'upload_type': 'image'}).sort('upload_date', -1))

    uploaded_files = {
        'pdf': pdf_files,
        'image': image_files
    }

    print(uploaded_files)

    return render_template('dashboard.html', user=user, uploaded_files=uploaded_files)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
