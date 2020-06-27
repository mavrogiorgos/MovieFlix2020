import json, os, sys
from pymongo import MongoClient

mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose MovieFlix database
db = client['MovieFlix']
users = db['Users']
movies = db['Movies']


def insert_all_users():
    users_list = []
    for line in open('./data/users.json', 'r'):
        users_list.append(json.loads(line))
    users.insert(users_list)    
    print("Users insertion completed")

def insert_all_movies():
    movies_list = []
    for line in open('./data/movies.json', 'r'):
        movies_list.append(json.loads(line))
    movies.insert(movies_list)    
    print("Movies insertion completed")