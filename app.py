from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import time
import os

app = Flask(__name__)
CORS(app)

CACHE_DURATION = 1000 
DATA_DIR = "data"

# Pastikan folder 'data' ada
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/')
def index():
    return jsonify({"message": "Gunakan endpoint /cuaca/<kode_lokasi> untuk mendapatkan data cuaca dari BMKG."})

@app.route('/cuaca/<kode_lokasi>')
def get_bmkg_weather(kode_lokasi):
    filepath = os.path.join(DATA_DIR, f"{kode_lokasi}.json")

    # Jika file cache ada dan belum kedaluwarsa
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            cached = json.load(f)
            if time.time() - cached['timestamp'] < CACHE_DURATION:
                return jsonify(cached['data'])

    # Scrape baru dari BMKG
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

            # Simpan ke file
            with open(filepath, 'w') as f:
                json.dump({
                    "timestamp": time.time(),
                    "data": nuxt_json
                }, f)

            return jsonify(nuxt_json)
        except json.JSONDecodeError:
            return jsonify({"error": "Gagal mem-parsing JSON dari tag __NUXT_DATA__"}), 500
    else:
        return jsonify({"error": "Tag <script id='__NUXT_DATA__'> tidak ditemukan"}), 404


@app.route('/cache')
def list_cache():
    files = os.listdir(DATA_DIR)
    return jsonify({"cached": files})

@app.route('/cache/<kode>')
def show_cache(kode):
    filepath = os.path.join(DATA_DIR, f"{kode}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({"error": "Cache not found"}), 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
