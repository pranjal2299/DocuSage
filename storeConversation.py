from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")  # Update the URI if needed
db = client["document_system"]
query_collection = db["queryStorage"]

def storingConversation (doc_id,user_query,model_reply,doc_name ):
    existing_chat = query_collection.find_one({"doc_id": doc_id})

    if not existing_chat:
        # Create new chat session with the first message as chatHeading
        chat_session = {
            "doc_id": doc_id,
            "doc_name":doc_name,
            "chatHeading": user_query,  # First question becomes the heading
            "conversation": []
        }
        query_collection.insert_one(chat_session)


    # Update the conversation array in MongoDB
    query_collection.update_one(
        {"doc_id": doc_id},
        {"$push": {"conversation": {"question": user_query, "answer": model_reply}}}
    )
