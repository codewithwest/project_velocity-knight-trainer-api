from flask import jsonify, request
from config import Connection
from app.utils import token_required, generate_username
from app.helpers import validate_image_upload, save_image_file, create_image_upload_record
from . import api

db = Connection.get_db()

@api.route('/user', methods=['GET'])
@token_required
def get_user(current_user_email):
    user = db.users.find_one({"email": current_user_email}, {'_id': 0, 'password': 0})
    return jsonify(user)

@api.route('/upload/image', methods=['POST'])
@token_required
def upload_image(current_user_email):
    validation_result, error = validate_image_upload(request)
    if error:
        return jsonify(validation_result), error

    file = validation_result['file']
    application_type = validation_result['application_type']

    try:
        user = db.users.find_one({"email": current_user_email})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_id = user['_id']

        file_url, filename = save_image_file(file)

        create_image_upload_record(db, current_user_email, user_id, application_type, file_url, filename)

        return jsonify({
            'message': 'Image uploaded successfully',
            'file': {
                'filename': filename,
                'url': file_url,
                'application_type': application_type
            }
        }), 201

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@api.route('/generate-username', methods=['GET'])
def get_username():
    """Returns a randomly generated username."""
    try:
        username = generate_username()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"username": username})
