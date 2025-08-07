from flask import Flask, redirect, request, send_file
from pymongo import MongoClient
from datetime import datetime
import os
import hashlib
import io

app = Flask(__name__)

# MongoDB com timeout de conexão
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://admin:******cluster0.tkda2dm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # timeout de 5s
db = client["rastreamento"]
collection = db["acessos"]

# Geração de hash curto
def gerar_hash(campanha, influenciador):
    base = f"{campanha.lower()}-{influenciador.lower()}"
    return hashlib.sha256(base.encode()).hexdigest()[:10]

# Rota de redirecionamento: /r/<hash>
@app.route("/r/<hash_id>")
def redirecionar(hash_id):
    user_agent = request.headers.get("User-Agent")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    timestamp = datetime.utcnow()

    collection.insert_one({
        "hash": hash_id,
        "ip": ip,
        "user_agent": user_agent,
        "timestamp": timestamp,
        "via": "redirect"
    })

    destino = "https://www.duzis.com.br"
    return redirect(destino, code=302)

# Rota de beacon invisível: /beacon/<influencer>/<campanha>.png
@app.route("/beacon/<influenciador>/<imagem>")
def beacon(influenciador, imagem):
    campanha = imagem.split(".")[0]
    hash_id = gerar_hash(campanha, influenciador)

    user_agent = request.headers.get("User-Agent")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    timestamp = datetime.utcnow()

    collection.insert_one({
        "hash": hash_id,
        "ip": ip,
        "user_agent": user_agent,
        "timestamp": timestamp,
        "via": "beacon"
    })

    # Retorna PNG invisível 1x1
    pixel = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01' \
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89' \
            b'\x00\x00\x00\nIDATx\xdacd\xf8\xff\xff?\x00\x05\xfe\x02' \
            b'\xfeA\x0e\x1b\xc4\x00\x00\x00\x00IEND\xaeB`\x82'
    return send_file(io.BytesIO(pixel), mimetype='image/png')

# Rota raiz
@app.route("/")
def home():
    return "✅ API de rastreamento de beacon invisível está online."
