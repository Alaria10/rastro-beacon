from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient
import hashlib

app = Flask(__name__)
CORS(app)

# Conexão com MongoDB
MONGO_URI = "mongodb+srv://admin:Duduzinho123@cluster0.tkda2dm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["rastro"]
campanhas = db["campanhas"]
conversoes = db["conversoes"]
visualizacoes = db["visualizacoes"]

@app.route("/")
def home():
    return "API do Rastro Beacon está online!"

@app.route("/conversao", methods=["POST"])
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

@app.route("/r/<campaign_hash>")
def redirecionar_campanha(campaign_hash):
    registro = campanhas.find_one({"hash": campaign_hash})

    if not registro:
        return "Campanha não encontrada", 404

    # Coleta dados do usuário
    ip = request.remote_addr
    ua = request.headers.get("User-Agent", "")
    timestamp = datetime.utcnow()

    raw = ip + ua
    fingerprint = hashlib.sha256(raw.encode()).hexdigest()

    conversoes.insert_one({
        "fingerprint": fingerprint,
        "user_agent": ua,
        "ip": ip,
        "timestamp": timestamp,
        "influencer": registro.get("influencer"),
        "campanha": registro.get("hash"),
        "url": registro.get("url")
    })

    return redirect(registro.get("url"), code=302)
