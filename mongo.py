import pymongo
from config import Auth

mongo = pymongo.MongoClient("mongodb+srv://{}:{}@{}/tests?retryWrites=true&w=majority".format(Auth.mongo_auth['username'], Auth.mongo_auth['auth']['debug'], Auth.mongo_auth['url']))
db = mongo.cp_new

def set(collection, id, data):
    i = {"_id":id}
    if db[collection].count_documents({"_id":id}) == 0:
        db[collection].insert_one({**i, **data})
    else:
        db[collection].update_one(i, {"$set":data})