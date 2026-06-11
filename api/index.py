import os
import time
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ==================== CONFIGURATION ====================
SUPABASE_URL = "https://lgnzuhfangjeqbosquaa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxnbnp1aGZhbmdqZXFib3NxdWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExODY4MzUsImV4cCI6MjA5Njc2MjgzNX0.-9i4JDnFweYUjGCTRJ0-cuhOAXpl97pIDarO3NvSV-s"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}
# =======================================================

TIMEOUT_THRESHOLD = 45 

# Route Utama: Membaca file index.html eksternal secara aman di Vercel
@app.route('/')
def dashboard():
    try:
        # Mencari lokasi file index.html yang berada satu folder dengan index.py
        base_dir = os.path.dirname(__file__)
        html_file_path = os.path.join(base_dir, 'index.html')
        
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return render_template_string(html_content)
    except Exception as e:
        return f"Gagal memuat halaman Frontend: {str(e)}", 500

# ==================== ENDPOINTS API ====================

@app.route('/api/ping', methods=['POST'])
def ping():
    data = request.json or {}
    account_name = data.get("account_name")
    device_note = data.get("device_note", "Unknown Device")
    
    if not account_name:
        return jsonify({"status": "error", "message": "Nama akun kosong"}), 400
    
    current_time = int(time.time())
    url = f"{SUPABASE_URL}/rest/v1/roblox_heartbeats"
    upsert_headers = HEADERS.copy()
    upsert_headers["Prefer"] = "resolution=merge-duplicates"
    
    payload = {"account_name": account_name, "device_note": device_note, "last_seen": current_time}
    
    try:
        res = requests.post(url, headers=upsert_headers, json=payload)
        if res.status_code in [200, 201, 204]:
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": res.text}), res.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/status-json', methods=['GET'])
def status_json():
    url = f"{SUPABASE_URL}/rest/v1/roblox_heartbeats"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            all_raw_data = res.json()
        else:
            return jsonify({"accounts": [], "total": 0, "online": 0, "offline": 0})
    except Exception:
        return jsonify({"accounts": [], "total": 0, "online": 0, "offline": 0})
    
    current_time = int(time.time())
    accounts_list = []
    online_count = 0
    offline_count = 0
    
    for row in all_raw_data:
        account = row.get("account_name")
        device_note = row.get("device_note")
        last_ping = int(row.get("last_seen", 0))
        time_diff = current_time - last_ping
        
        if time_diff <= TIMEOUT_THRESHOLD:
            status = "ONLINE"
            online_count += 1
            last_seen_text = "Baru saja"
        else:
            status = "OFFLINE"
            offline_count += 1
            mins = time_diff // 60
            if mins == 0:
                last_seen_text = f"{time_diff} detik lalu"
            elif mins < 60:
                last_seen_text = f"{mins} menit lalu"
            else:
                last_seen_text = f"{mins // 60} jam lalu"
                
        accounts_list.append({
            "name": account, "note": device_note, "status": status, "last_seen": last_seen_text
        })
        
    accounts_list.sort(key=lambda x: x['status'], reverse=False)
    return jsonify({
        "accounts": accounts_list, "total": len(accounts_list), "online": online_count, "offline": offline_count
    })


@app.route('/api/delete', methods=['POST'])
def delete_account():
    data = request.json or {}
    account_name = data.get("account_name")
    
    if not account_name:
        return jsonify({"status": "error", "message": "Nama akun kosong"}), 400
    
    url = f"{SUPABASE_URL}/rest/v1/roblox_heartbeats?account_name=eq.{account_name}"
    try:
        res = requests.delete(url, headers=HEADERS)
        if res.status_code in [200, 204]:
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": res.text}), res.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/edit', methods=['POST'])
def edit_device():
    data = request.json or {}
    account_name = data.get("account_name")
    new_note = data.get("new_note")
    
    if not account_name or not new_note:
        return jsonify({"status": "error", "message": "Data tidak lengkap"}), 400
    
    url = f"{SUPABASE_URL}/rest/v1/roblox_heartbeats?account_name=eq.{account_name}"
    try:
        res = requests.patch(url, headers=HEADERS, json={"device_note": new_note})
        if res.status_code in [200, 204]:
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": res.text}), res.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
