from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Gunakan endpoint /cuaca/<kode_lokasi> untuk mendapatkan data cuaca dari BMKG."})

@app.route('/cuaca/<kode_lokasi>', methods=['GET'])
def get_bmkg_weather(kode_lokasi):
    url = f"https://www.bmkg.go.id/cuaca/prakiraan-cuaca/{kode_lokasi}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    nuxt_data_tag = soup.find('script', {'id': '__NUXT_DATA__', 'type': 'application/json'})

    if nuxt_data_tag:
        try:
            nuxt_json = json.loads(nuxt_data_tag.string)
            return jsonify(nuxt_json)
        except json.JSONDecodeError:
            return jsonify({"error": "Gagal mem-parsing JSON dari tag __NUXT_DATA__"}), 500
    else:
        return jsonify({"error": "Tag <script id='__NUXT_DATA__'> tidak ditemukan"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
