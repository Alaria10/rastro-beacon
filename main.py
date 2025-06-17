from flask import Flask, redirect, request, send_file
from pymongo import MongoClient
from datetime import datetime
import os
import hashlib
import io

app = Flask(__name__)

# Conexão com o MongoDB (ajuste sua URL se estiver localmente ou fora do Railway)
MONGO_URI = "mongodb+srv://admin:Duduzinho123@cluster0.tkda2dm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["rastreamento"]
collection = db["acessos"]

# Função auxiliar para gerar o hash
def gerar_hash(campanha, influenciador):
    base = f"{campanha.lower()}-{influenciador.lower()}"
    return hashlib.sha256(base.encode()).hexdigest()[:10]

# Exemplo de URL rastreável: /r/abc123def0
@app.route("/r/<hash_id>")
def redirecionar(hash_id):
    user_agent = request.headers.get("User-Agent")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    timestamp = datetime.utcnow()

    # Salva o acesso no MongoDB
    collection.insert_one({
        "hash": hash_id,
        "ip": ip,
        "user_agent": user_agent,
        "timestamp": timestamp,
        "via": "redirect"
    })

    # Aqui você pode fazer o mapeamento do hash para a URL de destino real
    destino = "https://www.duzis.com.br"  # exemplo fixo, pode virar lookup de hash -> URL depois
    return redirect(destino, code=302)

# Rota de beacon invisível: /beacon/@influencer/nome-da-campanha.png
@app.route("/beacon/<influenciador>/<imagem>")
def beacon(influenciador, imagem):
    campanha = imagem.split(".")[0]  # remove ".png"
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

    # Retorna uma imagem PNG invisível de 1x1 pixel
    pixel = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01' \
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89' \
            b'\x00\x00\x00\nIDATx\xdacd\xf8\xff\xff?\x00\x05\xfe\x02' \
            b'\xfeA\x0e\x1b\xc4\x00\x00\x00\x00IEND\xaeB`\x82'
    return send_file(io.BytesIO(pixel), mimetype='image/png')

@app.route("/")
def home():
    return "✅ API de rastreamento de beacon invisível está online."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
