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

# HTML Dashboard UI dengan Font Awesome & Fitur Edit/Delete
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemstones Monitor - Multi Account Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
    </style>
</head>
<body class="bg-[#0f172a] text-slate-100 min-h-screen">
    <div class="max-w-6xl mx-auto px-4 py-8">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-800 pb-6 mb-8 gap-4">
            <div>
                <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">Gemstones Hub Monitor</h1>
                <p class="text-slate-400 text-sm mt-1">Sistem backend sekarang didukung oleh Supabase REST API</p>
            </div>
            <div class="bg-slate-800/50 backdrop-blur px-4 py-2 rounded-xl border border-slate-700/50 text-sm flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Auto Refresh: <span class="font-semibold text-blue-400">5s</span></span>
            </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8">
            <div class="bg-slate-800/40 p-4 rounded-xl border border-slate-700/30">
                <p class="text-xs text-slate-400 uppercase tracking-wider font-semibold">Total Terdaftar</p>
                <p id="stat-total" class="text-2xl font-bold mt-1 text-slate-200">0</p>
            </div>
            <div class="bg-emerald-950/20 p-4 rounded-xl border border-emerald-500/20">
                <p class="text-xs text-emerald-400 uppercase tracking-wider font-semibold">Online</p>
                <p id="stat-online" class="text-2xl font-bold mt-1 text-emerald-400">0</p>
            </div>
            <div class="bg-rose-950/20 p-4 rounded-xl border border-rose-500/20 col-span-2 sm:col-span-1">
                <p class="text-xs text-rose-400 uppercase tracking-wider font-semibold">Offline</p>
                <p id="stat-offline" class="text-2xl font-bold mt-1 text-rose-400">0</p>
            </div>
        </div>

        <div id="accounts-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div class="col-span-full text-center py-12 text-slate-500">Memuat data dari Supabase...</div>
        </div>
    </div>

    <script>
        // Fungsi Hapus Akun
        async function deleteAccount(name) {
            if (!confirm(`Yakin ingin menghapus akun '${name}' dari database?`)) return;
            try {
                const res = await fetch('/api/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account_name: name })
                });
                const result = await res.json();
                if (result.status === 'success') {
                    fetchStatus(); // Langsung refresh data
                } else {
                    alert('Gagal menghapus: ' + result.message);
                }
            } catch (e) {
                alert('Terjadi kesalahan jaringan!');
            }
        }

        // Fungsi Edit Device Note
        async function editDevice(name, currentNote) {
            const newNote = prompt(`Ubah catatan device untuk '${name}':`, currentNote);
            if (newNote === null || newNote.trim() === '' || newNote === currentNote) return;
            try {
                const res = await fetch('/api/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account_name: name, new_note: newNote.trim() })
                });
                const result = await res.json();
                if (result.status === 'success') {
                    fetchStatus(); // Langsung refresh data
                } else {
                    alert('Gagal mengedit: ' + result.message);
                }
            } catch (e) {
                alert('Terjadi kesalahan jaringan!');
            }
        }

        async function fetchStatus() {
            try {
                const res = await fetch('/api/status-json');
                const data = await res.json();
                
                document.getElementById('stat-total').innerText = data.total;
                document.getElementById('stat-online').innerText = data.online;
                document.getElementById('stat-offline').innerText = data.offline;

                const grid = document.getElementById('accounts-grid');
                grid.innerHTML = '';

                if (!data.accounts || data.accounts.length === 0) {
                    grid.innerHTML = `<div class="col-span-full text-center py-12 text-slate-500 bg-slate-800/20 rounded-xl border border-slate-800">Belum ada data di database Supabase. Jalankan script client di Roblox.</div>`;
                    return;
                }

                data.accounts.forEach(acc => {
                    const statusConfig = acc.status === 'ONLINE' 
                        ? { bg: 'bg-emerald-500/10 border-emerald-500/30', badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', text: 'Online' }
                        : { bg: 'bg-slate-800/30 border-slate-800', badge: 'bg-slate-700/30 text-slate-400 border-slate-600/30', text: 'Offline' };

                    // Melindungi tanda kutip agar tidak merusak JS
                    const safeNote = acc.note.replace(/'/g, "\\'");

                    const card = `
                        <div class="p-5 rounded-xl border transition-all duration-300 ${statusConfig.bg} relative group">
                            <div class="flex justify-between items-start mb-4">
                                <div class="overflow-hidden mr-2">
                                    <h3 class="font-bold text-slate-200 truncate" title="${acc.name}">${acc.name}</h3>
                                    <div class="text-xs text-slate-400 mt-1 flex items-center gap-2 truncate">
                                        <span>📱 ${acc.note}</span>
                                        <button onclick="editDevice('${acc.name}', '${safeNote}')" class="text-slate-500 hover:text-blue-400 transition-colors" title="Edit Device">
                                            <i class="fa-solid fa-pen-to-square"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="flex flex-col items-end gap-3">
                                    <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold border ${statusConfig.badge}">
                                        ${statusConfig.text}
                                    </span>
                                    <button onclick="deleteAccount('${acc.name}')" class="text-slate-500 opacity-60 hover:opacity-100 hover:text-rose-500 transition-all" title="Hapus Akun">
                                        <i class="fa-solid fa-trash-can text-sm"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="text-xs text-slate-500 flex justify-between border-t border-slate-800/60 pt-3 mt-2">
                                <span>Terakhir Aktif:</span>
                                <span class="text-slate-400 font-medium">${acc.last_seen}</span>
                            </div>
                        </div>
                    `;
                    grid.innerHTML += card;
                });

            } catch (err) {
                console.error("Gagal update data:", err);
            }
        }
        fetchStatus();
        setInterval(fetchStatus, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

# ==================== ENDPOINTS DATA ====================

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

# ==================== ENDPOINTS BARU: HAPUS & EDIT ====================

@app.route('/api/delete', methods=['POST'])
def delete_account():
    data = request.json or {}
    account_name = data.get("account_name")
    
    if not account_name:
        return jsonify({"status": "error", "message": "Nama akun kosong"}), 400
    
    # URL dengan query parameter 'eq' (equals) untuk mencari nama akun yang spesifik
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
        # Patch digunakan untuk mengupdate kolom tertentu (device_note) tanpa mengubah last_seen
        res = requests.patch(url, headers=HEADERS, json={"device_note": new_note})
        if res.status_code in [200, 204]:
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": res.text}), res.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
