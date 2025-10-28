import os
from werkzeug.utils import secure_filename
from vercel_blob import put
import datetime

# Define the local upload folder
LOCAL_UPLOADS = os.path.join(os.getcwd(), 'app', 'static', 'uploads')

def validate_image_upload(request):
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    application_type = request.form.get('application_type')
    if not application_type:
        return {'error': 'application_type is required'}, 400

    return {'file': file, 'application_type': application_type}, None

def save_image_file(file):
    filename = secure_filename(file.filename)
    is_vercel = os.environ.get('VERCEL')
    upload_type = 'image'

    if is_vercel:
        blob_result = put(filename, file.read(), options={'access': 'public'})
        return blob_result['url'], filename
    else:
        image_upload_path = os.path.join(LOCAL_UPLOADS, upload_type)
        if not os.path.exists(image_upload_path):
            os.makedirs(image_upload_path)
        file_path = os.path.join(image_upload_path, filename)
        file.save(file_path)
        return f'/static/uploads/{upload_type}/{filename}', filename

def create_image_upload_record(db_connection, user_email, user_id, application_type, file_url, filename):
    now = datetime.datetime.utcnow()
    upload_record = {
        'filename': filename,
        'url': file_url,
        'upload_type': 'image',
        'user_email': user_email,
        'user_id': user_id,
        'application_type': application_type,
        'created_at': now,
        'updated_at': now
    }
    db_connection.get_collection('uploads').insert_one(upload_record)
    return upload_record
