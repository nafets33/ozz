from pymongo import MongoClient

def connect_to_mongodb(connection_string, database_name, collection_name):
    client = MongoClient(connection_string)
    db = client[database_name]
    collection = db[collection_name]
    return collection

def insert_document(collection, document):
    result = collection.insert_one(document)
    return result.inserted_id

def find_document(collection, query):
    result = collection.find_one(query)
    return result

def update_document(collection, filter_criteria, update_data):
    result = collection.update_one(filter_criteria, {"$set": update_data})
    return result.modified_count

def delete_document(collection, delete_criteria):
    result = collection.delete_one(delete_criteria)
    return result.deleted_count

def get_all_documents(collection):
    documents = collection.find()
    return list(documents)


def get_last_num_documents(collection, limit_n=100):
    documents = collection.find().sort([('_id', -1)]).limit(limit_n)
    return list(documents)