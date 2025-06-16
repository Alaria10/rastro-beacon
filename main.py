from flask import Flask, request, send_file
from hashlib import sha256
from datetime import datetime
import pymongo
import io

app = Flask(__name__)

MONGO_URI = "mongodb+srv://admin:Duduzinho123@cluster0.tkda2dm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGO_URI)
db = client["rastro"]
colecao = db["visualizacoes"]

@app.route('/beacon/<influencer>/<campanha>.png')
def beacon(influencer, campanha):
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    timestamp = datetime.utcnow()

    fingerprint = sha256(f"{ip}|{user_agent}".encode()).hexdigest()

    colecao.insert_one({
        "fingerprint": fingerprint,
        "ip": ip,
        "user_agent": user_agent,
        "influencer": influencer,
        "campanha": campanha,
        "timestamp": timestamp
    })

    pixel = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01' \
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4' \
            b'\x89\x00\x00\x00\nIDATx\xdac\x00\x01\x00\x00\x05' \
            b'\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    return send_file(io.BytesIO(pixel), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
