import os

from gridfs import GridFS
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "bookvisualizer"

client = MongoClient(MONGO_URI)
database = client[DATABASE_NAME]

grid_fs = GridFS(database)
