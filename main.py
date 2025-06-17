from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MongoDB
MONGO_URI = "mongodb+srv://admin:Duduzinho123@cluster0.tkda2dm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["rastro"]
campanhas = db["campanhas"]
conversoes = db["conversoes"]
visualizacoes = db["visualizacoes"]

@app.route('/')
def home():
    return "API do Rastro Beacon está online!"

@app.route('/r/<hash>')
def redirecionar(hash):
    campanha = campanhas.find_one({"hash": hash})
    if not campanha:
        return "Campanha não encontrada", 404

    # Gera script para salvar no localStorage (executado como imagem invisível)
    html = f"""
    <html>
    <head><meta http-equiv="refresh" content="0; url={campanha['url']}"></head>
    <body>
    <script>
      localStorage.setItem("rastro_influencer", "{campanha['influencer']}");
      localStorage.setItem("rastro_campanha", "{campanha['campanha']}");
    </script>
    </body>
    </html>
    """
    return html

@app.route('/conversao', methods=['POST'])
def registrar_conversao():
    data = request.get_json()
    fingerprint = data.get("fingerprint")
    url = data.get("url")
    influencer = data.get("influencer")
    campanha = data.get("campanha")
    timestamp = datetime.utcnow()

    if not fingerprint or not url:
        return jsonify({"erro": "Dados incompletos"}), 400

    conversoes.insert_one({
        "fingerprint": fingerprint,
        "url": url,
        "timestamp": timestamp,
        "influencer": influencer,
        "campanha": campanha
    })

    return jsonify({"status": "ok"})
