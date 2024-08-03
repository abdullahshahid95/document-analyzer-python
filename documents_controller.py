import os
import uuid
from flask import request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app as app
from werkzeug.exceptions import BadRequest
import re

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_document(req):
    if 'file' not in req.files:
        return jsonify({'error': 'No file part'}), 400

    file = req.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF and Word files are allowed.'}), 400

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f'document_{uuid.uuid4()}.{file_ext}'
    file_path = os.path.join(UPLOAD_FOLDER, new_filename)
    file.save(file_path)
    
    return jsonify({'file_name': new_filename}), 200

def query_document(req):
    from cerberus import Validator
    v = Validator()

    schema = {
        'type': {'type': 'string', 'allowed': ['summary', 'entity_extraction', 'question_answer'], 'required': True},
        'query': {'type': 'string', 'required': True},
    }

    query = req.args.to_dict()
    if not v.validate(query, schema):
        return jsonify({'message': 'Validation error', 'error': v.errors}), 400

    type = query['type']
    queryText = query['query']
    return jsonify({'data': {'type': type, 'query': queryText, 'response': 'This is query response', 'precision': 2.2}}), 200
