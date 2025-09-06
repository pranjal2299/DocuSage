from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import uuid
import os
from storingEmbedding import process_pdf
# from imagequerying import vision_model
from retrievingQueryResponse import retrievingReponse
from storeConversation import storingConversation


app = Flask(__name__)
CORS(app) 

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/") 
db = client["document_system"]
docs_collection = db["documents"]
query_collection = db["queryStorage"]

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
IMAGE_EXTENSIONS = {".png", ".svg", ".jpeg", ".jpg"}

@app.route("/getDoc", methods=["GET"])
def retireveAllDoc ():
    documents = list(docs_collection.find({}, {"_id": 0}))  # Exclude `_id`
    return jsonify(documents)

@app.route("/upload", methods=["POST"])
def upload_document():
    """Upload a document (PDF or Image), generate a unique ID, and store metadata."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in IMAGE_EXTENSIONS and file_ext != ".pdf":
        return jsonify({"error": "Unsupported file type."}), 400
    
    doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    doc_type = "pdf" if file_ext == ".pdf" else "image"

    # Store metadata in MongoDB
    docs_collection.insert_one({
        "doc_id": doc_id,
        "doc_name": file.filename,
        "doc_type": file_ext,
        "file_path": file_path,
        "doc_Category" :doc_type
    })

    if file_ext == ".pdf":
        process_pdf(doc_id, file_path)

    return jsonify({
        "message": "Document uploaded successfully.",
        "doc_id": doc_id,
        "doc_name": file.filename,
        "doc_type": file_ext
    }), 201

@app.route("/askBot", methods=["POST"])
def retrieve_answer():
    print("dfghjkl")
    """Retrieve an answer for the given query (text-based or image-based)."""
    data = request.json

    userId = data.get('userId')
    userName = data.get('userName')
    query = data.get('query')
    docId = data.get('doc_id')

    # Get document details from MongoDB
    doc_info = docs_collection.find_one({"doc_id": docId})
    chat_info = query_collection.find_one({"doc_id":docId})

    if not doc_info:
        return jsonify({"error": "Document ID not found"}), 404
    
    file_type = doc_info["doc_type"]
    file_path = doc_info["file_path"]
    doc_name = doc_info['doc_name']
    conversation_history = chat_info['conversation']

    if file_type == ".pdf":
        response = retrievingReponse(docId, query, conversation_history)
    elif file_type in IMAGE_EXTENSIONS:
        response = vision_model(file_path, query)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    
    storingConversation(docId,query,response,doc_name)

    return jsonify({
        "question":query,
        "answer": response,
        "doc_id": docId
    }), 201


@app.route("/getChat", methods=["GET"])
def get_chats():
    
    doc_id = request.args.get("doc_id") 

    if doc_id:
        # Fetch complete chat history for the given doc_id
        chat_session = query_collection.find_one({"doc_id": doc_id}, {"_id": 0})
        if not chat_session:
            return jsonify({"error": "No chat found for this document"}), 404
        return jsonify(chat_session)

    else:
        # Fetch only doc_id and chatHeading for all documents
        all_chats = list(query_collection.find({}, {"_id": 0, "doc_id": 1, "chatHeading": 1,"doc_name":1}))
        return jsonify({"chats": all_chats})

@app.route("/deleteDoc", methods=["DELETE"])
def delete_document():
    """Delete a document and its associated data."""
    doc_id = request.args.get("doc_id")

    if not doc_id:
        return jsonify({"error": "Missing doc_id"}), 400

    doc_info = docs_collection.find_one({"doc_id": doc_id})
    if not doc_info:
        return jsonify({"error": "Document not found"}), 404

    # Delete physical file
    file_path = doc_info.get("file_path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    # Delete from MongoDB
    docs_collection.delete_one({"doc_id": doc_id})
    query_collection.delete_many({"doc_id": doc_id})  # for all chats of that doc

    return jsonify({"message": "Document and related data deleted successfully."}), 200

@app.route("/viewDoc", methods=["GET"])
def view_doc():
    doc_name = request.args.get("docName")
    if not doc_name:
        return jsonify({"error": "Missing doc_name"}), 400

    # Optional: check if file actually exists
    file_path = os.path.join(UPLOAD_FOLDER, doc_name)
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404

    return jsonify({
        "url": f"/uploads/{doc_name}"
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
