import os
import requests
from flask import render_template, request, redirect, url_for, current_app
from . import main

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN')
            if blob_token:
                # Upload to Vercel Blob
                headers = {
                    'Authorization': f'Bearer {blob_token}',
                    'x-vercel-blob-access': 'public',
                }
                response = requests.put(
                    f'https://blob.vercel-storage.com/{file.filename}',
                    headers=headers,
                    data=file.read()
                )
                response.raise_for_status()
            else:
                # Save locally
                filename = file.filename
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
            return redirect(url_for('main.index'))
    return render_template('index.html')
