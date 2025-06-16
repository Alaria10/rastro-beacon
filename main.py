from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient
import hashlib
from io import BytesIO
from PIL import Image

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

@app.route('/beacon/<influencer>/<campanha>.png')
def registrar_visualizacao(influencer, campanha):
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "")
    raw = ip + user_agent
    fingerprint = hashlib.sha256(raw.encode()).hexdigest()

    visualizacoes.insert_one({
        "fingerprint": fingerprint,
        "ip": ip,
        "user_agent": user_agent,
        "influencer": f"@{influencer}",
        "campanha": campanha,
        "timestamp": datetime.utcnow()
    })

    print(f"[BEACON] Visualização registrada: {fingerprint} ({influencer}/{campanha})")

    # Retorna imagem invisível 1x1
    pixel = BytesIO()
    Image.new("RGB", (1, 1)).save(pixel, "PNG")
    pixel.seek(0)
    return send_file(pixel, mimetype='image/png')
