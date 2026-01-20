from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["school_db"]
collection = db["students"]

def add_student(student):
    collection.insert_one(student.__dict__)
