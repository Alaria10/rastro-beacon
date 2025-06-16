from flask import Flask, request, jsonify, send_file
from datetime import datetime
from pymongo import MongoClient
import io

app = Flask(__name__)

# Conexão com MongoDB
MONGO_URI = "mongodb+srv://admin:Duduzinho123@cluster0.tkda2dm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["rastro"]
visualizacoes = db["visualizacoes"]
conversoes = db["conversoes"]

@app.route("/")
def home():
    return "API do Rastro Beacon está online!"

@app.route('/beacon/<influencer>/<campanha>.png')
def beacon(influencer, campanha):
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    timestamp = datetime.utcnow()

    # fingerprint básico gerado a partir do IP + user-agent
    import hashlib
    fingerprint = hashlib.sha256(f"{ip}{user_agent}".encode()).hexdigest()

    visualizacoes.insert_one({
        "fingerprint": fingerprint,
        "ip": ip,
        "user_agent": user_agent,
        "influencer": influencer,
        "campanha": campanha,
        "timestamp": timestamp
    })

    # Gera pixel invisível (1x1 transparente)
    pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21' \
            b'\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02' \
            b'\x44\x01\x00\x3B'
    return send_file(io.BytesIO(pixel), mimetype='image/gif')

@app.route('/conversao', methods=['POST'])
def conversao():
    data = request.get_json()
    fingerprint = data.get("fingerprint")
    url = data.get("url")
    timestamp = datetime.utcnow()

    if not fingerprint:
        return jsonify({"status": "erro", "mensagem": "Fingerprint ausente"}), 400

    visualizou = visualizacoes.find_one({"fingerprint": fingerprint})

    conversoes.insert_one({
        "fingerprint": fingerprint,
        "url": url,
        "timestamp": timestamp,
        "influencer": visualizou["influencer"] if visualizou else None,
        "campanha": visualizou["campanha"] if visualizou else None,
        "foi_influenciado": bool(visualizou)
    })

    return jsonify({"status": "ok", "foi_influenciado": bool(visualizou)})

if __name__ == '__main__':
    app.run(debug=True)
