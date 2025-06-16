from flask import Flask, request, jsonify
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)

# Conexão com MongoDB
MONGO_URI = "mongodb+srv://admin:Duduzinho123@cluster0.tkda2dm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["rastro"]
visualizacoes = db["visualizacoes"]
conversoes = db["conversoes"]

@app.route('/')
def home():
    return 'API do Rastro Beacon está online!'

@app.route('/conversao', methods=['POST'])
def conversao():
    data = request.get_json()
    fingerprint = data.get("fingerprint")
    url = data.get("url")
    timestamp = datetime.utcnow()

    if not fingerprint:
        return jsonify({"status": "erro", "mensagem": "Fingerprint ausente"}), 400

    # Verifica se esse fingerprint já viu algum story
    visualizou = visualizacoes.find_one({"fingerprint": fingerprint})

    # Registra como conversão mesmo que não tenha visto o story
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
