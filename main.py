from flask import Flask, request
from flask_cors import CORS
from documents_controller import upload_document, query_document

app = Flask(__name__)
CORS(app)

port = 3000

@app.route('/document/upload', methods=['POST'])
def upload_document_route():
    return upload_document(request)

@app.route('/document/query', methods=['GET'])
def query_document_route():
    return query_document(request)

if __name__ == '__main__':
    app.run(port=port, debug=True)
