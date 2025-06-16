from flask import Flask, request, jsonify, redirect
from datetime import datetime
from pymongo import MongoClient
from hashlib import sha256

app = Flask(__name__)

# Conexão com MongoDB
MONGO_URI = "mongodb+srv://admin:Duduzinho123@cluster0.tkda2dm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["rastro"]

visualizacoes = db["visualizacoes"]
conversoes = db["conversoes"]
campanhas = db["campanhas"]

@app.route("/")
def home():
    return "API do Rastro Beacon está online!"

@app.route('/beacon/<influencer>/<campanha>.png')
def beacon(influencer, campanha):
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    timestamp = datetime.utcnow()

    fingerprint = sha256(f"{ip}{user_agent}".encode()).hexdigest()

    visualizacoes.insert_one({
        "fingerprint": fingerprint,
        "ip": ip,
        "user_agent": user_agent,
        "influencer": f"@{influencer}",
        "campanha": campanha,
        "timestamp": timestamp
    })

    from flask import send_file
    import io
    return send_file(io.BytesIO(b""), mimetype='image/png')

@app.route("/r/<campaign_hash>")
def track_and_redirect(campaign_hash):
    campanha = campanhas.find_one({"hash": campaign_hash})
    if not campanha:
        return "Campanha não encontrada", 404

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "")
    referrer = request.headers.get("Referer", "")
    timestamp = datetime.utcnow()

    fingerprint = sha256(f"{ip}{user_agent}".encode()).hexdigest()

    conversoes.insert_one({
        "fingerprint": fingerprint,
        "timestamp": timestamp,
        "referrer": referrer,
        "influencer": campanha.get("influencer"),
        "campaign_hash": campaign_hash
    })

    return redirect(campanha["url"], code=302)

if __name__ == '__main__':
    app.run(debug=True)
