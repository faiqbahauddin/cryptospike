import os, json, requests

TOKEN = os.environ["TG_TOKEN"]
CHAT_ID = os.environ["TG_CHAT_ID"]
SIGNAL_URL = os.environ["SIGNAL_URL"]
STATE = "seen.json"

def cari_sinyal(x):
    """Cari list objek yang punya 'id' dan 'symbol', di struktur JSON apa pun."""
    if isinstance(x, list):
        if x and all(isinstance(i, dict) for i in x) and any("symbol" in i and "id" in i for i in x):
            return [i for i in x if "symbol" in i and "id" in i]
        hasil = []
        for i in x:
            hasil += cari_sinyal(i)
        return hasil
    if isinstance(x, dict):
        if "symbol" in x and "id" in x:
            return [x]
        hasil = []
        for v in x.values():
            hasil += cari_sinyal(v)
        return hasil
    return []

def kirim(s):
    teks = (
        f"🚨 {s.get('symbol')} {s.get('side')} ({s.get('strength', '-')})\n"
        f"Entry: {s.get('entryPrice')}\n"
        f"TP1: {s.get('tp1')}\n"
        f"TP2: {s.get('tp2')}\n"
        f"TP3: {s.get('tp3')}\n"
        f"SL: {s.get('sl')}\n"
        f"Score: {s.get('score')} | {s.get('strategy', '-')}\n"
        f"Status: {s.get('status')}\n"
        f"{s.get('reasons', '')}"
    )
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": teks},
        timeout=15,
    )

r = requests.get(SIGNAL_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
r.raise_for_status()
sinyal = cari_sinyal(r.json())
ids = {str(s["id"]) for s in sinyal}

seen = set(json.load(open(STATE))) if os.path.exists(STATE) else None

if seen is None:
    seen = ids          # run pertama: simpan saja, tidak kirim apa-apa
else:
    baru = [s for s in sinyal if str(s["id"]) not in seen]
    for s in baru[:10]:  # maksimal 10 pesan per run
        kirim(s)
    seen |= ids

json.dump(sorted(seen), open(STATE, "w"))
print(f"Total sinyal: {len(sinyal)}")
