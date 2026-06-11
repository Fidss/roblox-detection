import time
from flask import Flask, request, jsonify, render_template_string
from supabase import create_client, Client

app = Flask(__name__)

# ==================== CONFIGURATION (DEVELOPMENT ONLY) ====================
# Taruh link dan anon key public Supabase kamu di bawah ini:
SUPABASE_URL = "https://lgnzuhfangjeqbosquaa.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxnbnp1aGZhbmdqZXFib3NxdWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExODY4MzUsImV4cCI6MjA5Njc2MjgzNX0.-9i4JDnFweYUjGCTRJ0-cuhOAXpl97pIDarO3NvSV-s"
# ==========================================================================

# Inisialisasi client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TIMEOUT_THRESHOLD = 45 

# HTML Dashboard UI
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemstones Monitor - Multi Account Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
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
                <p class="text-slate-400 text-sm mt-1">Sistem backend sekarang didukung oleh Supabase PostgreSQL</p>
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
        async function fetchStatus() {
            try {
                const res = await fetch('/api/status-json');
                const data = await res.json();
                
                document.getElementById('stat-total').innerText = data.total;
                document.getElementById('stat-online').innerText = data.online;
                document.getElementById('stat-offline').innerText = data.offline;

                const grid = document.getElementById('accounts-grid');
                grid.innerHTML = '';

                if (data.accounts.length === 0) {
                    grid.innerHTML = `<div class="col-span-full text-center py-12 text-slate-500 bg-slate-800/20 rounded-xl border border-slate-800">Belum ada data di database Supabase. Jalankan script client.</div>`;
                    return;
                }

                data.accounts.forEach(acc => {
                    const statusConfig = acc.status === 'ONLINE' 
                        ? { bg: 'bg-emerald-500/10 border-emerald-500/30', badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', text: 'Online' }
                        : { bg: 'bg-slate-800/30 border-slate-800', badge: 'bg-slate-700/30 text-slate-400 border-slate-600/30', text: 'Offline' };

                    const card = `
                        <div class="p-5 rounded-xl border transition-all duration-300 ${statusConfig.bg}">
                            <div class="flex justify-between items-start mb-4">
                                <div class="overflow-hidden mr-2">
                                    <h3 class="font-bold text-slate-200 truncate" title="${acc.name}">${acc.name}</h3>
                                    <p class="text-xs text-slate-400 mt-1 truncate">📱 ${acc.note}</p>
                                </div>
                                <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold border ${statusConfig.badge}">
                                    ${statusConfig.text}
                                </span>
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

# Endpoint Menerima Data dari Roblox
@app.route('/api/ping', methods=['POST'])
def ping():
    data = request.json or {}
    account_name = data.get("account_name")
    device_note = data.get("device_note", "Unknown Device")
    
    if not account_name:
        return jsonify({"status": "error", "message": "Nama akun kosong"}), 400
    
    current_time = int(time.time())
    
    try:
        # Menyimpan atau menimpa data berdasarkan account_name (Upsert)
        supabase.table('roblox_heartbeats').upsert({
            "account_name": account_name,
            "device_note": device_note,
            "last_seen": current_time
        }).execute()
        
        return jsonify({"status": "success", "message": f"Ping sukses untuk {account_name}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint Data Mentah untuk Dashboard Frontend
@app.route('/api/status-json', methods=['GET'])
def status_json():
    try:
        response = supabase.table('roblox_heartbeats').select("*").execute()
        all_raw_data = response.data
    except Exception as e:
        return jsonify({"accounts": [], "total": 0, "online": 0, "offline": 0, "error": str(e)})
    
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
            "name": account,
            "note": device_note,
            "status": status,
            "last_seen": last_seen_text
        })
        
    accounts_list.sort(key=lambda x: x['status'], reverse=False)
        
    return jsonify({
        "accounts": accounts_list,
        "total": len(accounts_list),
        "online": online_count,
        "offline": offline_count
    })
    
