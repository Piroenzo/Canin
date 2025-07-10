from pymongo import MongoClient
import os

uri = os.getenv('MONGO_URI', 'mongodb+srv://caninexpresss:2fwSHK2aSUV6CYd8@canin.jc5eowy.mongodb.net/Canin?retryWrites=true&w=majority&appName=Canin')
client = MongoClient(uri)
try:
    db = client["Canin"]
    print("Colecciones:", db.list_collection_names())
    print("¡Conexión exitosa!")
except Exception as e:
    print("Error de conexión:", e) 