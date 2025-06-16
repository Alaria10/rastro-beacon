from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # <-- ATIVA O CORS PARA TODOS OS DOMÍNIOS

# MongoDB
MONGO_URI = "mongodb+srv://admin:Duduzinho123@cluster0.tkda2dm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["rastro"]
campanhas = db["campanhas"]
conversoes = db["conversoes"]

@app.route('/')
def home():
    return "API do Rastro Beacon está online!"

@app.route('/conversao', methods=['POST'])
def registrar_conversao():
    data = request.get_json()
    fingerprint = data.get("fingerprint")
    url = data.get("url")
    timestamp = datetime.utcnow()

    if not fingerprint or not url:
        return jsonify({"erro": "Dados incompletos"}), 400

    conversoes.insert_one({
        "fingerprint": fingerprint,
        "url": url,
        "timestamp": timestamp
    })

    return jsonify({"status": "ok"})
