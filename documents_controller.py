import os
import uuid
from flask import request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app as app
from werkzeug.exceptions import BadRequest
import re 
from summary import process_file

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
    
    text, summary, entities = process_file("./uploads/" + new_filename, file_ext, 0)

    sanitized = ""

    if entities:
        sanitized = entities.split("Entities:\n- ")
        if(len(sanitized) > 1):
            sanitized = sanitized[1].strip()
            if sanitized:
                sanitized = sanitized.split("\n- ")
        else:
            sanitized = ""

    return jsonify({'file_name': new_filename, 'summary': summary, 'entities': sanitized}), 200

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
    
    # Define response texts based on the type
    responses = {
        'summary': "In Q2, our sales performance demonstrated a significant improvement compared to Q1, with a 15% increase in overall revenue. This growth was primarily driven by the successful launch of the X series and Y series products, which collectively accounted for 60% of the total revenue. Additionally, our customer acquisition efforts proved effective, resulting in a 10% rise in new customer accounts. The repeat purchase rate also saw a positive trend, indicating increased customer satisfaction and loyalty. The quarter was marked by several strategic marketing campaigns and product promotions that contributed to these positive results.",
        'entity_extraction': "The document references several companies, including Acme Corp, Beta Industries, and Gamma Solutions. Acme Corp is highlighted as the primary client, with whom we have a major ongoing contract and significant business dealings. Beta Industries is listed as a secondary partner involved in the supply chain, contributing components and services essential to our operations. Gamma Solutions, another key player, provides specialized software solutions that support our analytics and reporting needs. These companies play crucial roles in our business ecosystem and are integral to our supply and service networks.",
        'question_answer': "The sales report outlines several key dates that are crucial for understanding the performance and planning future strategies. The fiscal year began on January 1st, marking the start of the reporting period. The end of Q1 was on March 31st, which was used for preliminary performance assessments and strategic adjustments. Q2 ended on June 30th, providing a mid-year review of sales achievements and areas for improvement. The final report date is December 31st, which encompasses the full fiscal year and allows for a comprehensive analysis of annual performance. Additionally, significant product launch dates and major sales events are highlighted throughout the year, such as the launch of the X series on April 15th and the annual sales summit held on September 10th."
    }

    type = query['type']
    response_text = responses.get(type, 'Unknown type')
    queryText = query['query']
    return jsonify({'data': {'type': type, 'query': queryText, 'response': response_text, 'precision': 2.2}}), 200
