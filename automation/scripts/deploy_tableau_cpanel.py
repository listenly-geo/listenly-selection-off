"""Envoie les fichiers du tableau de suivi sur listenly.org par l'API cPanel (UAPI Fileman/upload_files).
Utilise : CPANEL_USER, CPANEL_TOKEN (secrets), CPANEL_HOST (defaut pendule.o2switch.net), CPANEL_DIR (defaut listenly.fr/podcast-btb).
N'ecrit jamais de secret dans un fichier ni dans le journal. Sort en code 1 si un envoi echoue."""
import os, sys, requests
HOST = os.environ.get("CPANEL_HOST") or "pendule.o2switch.net"
USER, TOKEN = os.environ.get("CPANEL_USER", ""), os.environ.get("CPANEL_TOKEN", "")
BASE = (os.environ.get("CPANEL_DIR") or "listenly.fr/podcast-btb").strip("/")
SRC = "_tableau"
if not USER or not TOKEN:
    print("CPANEL_USER / CPANEL_TOKEN absents"); sys.exit(1)
H = {"Authorization": f"cpanel {USER}:{TOKEN}"}
home = None
r = requests.get(f"https://{HOST}:2083/execute/Fileman/get_file_information", headers=H, params={"path": "."}, timeout=60)
base = BASE
try:
    q = requests.get(f"https://{HOST}:2083/execute/Variables/get_user_information", headers=H, timeout=60).json()
    home = (q.get("data") or {}).get("home")
except Exception:
    pass
if home:
    base = f"{home}/{BASE}"
bad = 0
for root, _, files in os.walk(SRC):
    for f in files:
        p = os.path.join(root, f)
        rel = os.path.relpath(root, SRC)
        d = base if rel == "." else f"{base}/{rel}"
        with open(p, "rb") as fh:
            resp = requests.post(f"https://{HOST}:2083/execute/Fileman/upload_files", headers=H,
                                 data={"dir": d, "overwrite": "1"}, files={"file-1": (f, fh)}, timeout=180)
        try:
            j = resp.json()
        except Exception:
            j = {}
        ok = resp.status_code == 200 and j.get("status") == 1
        print(("OK  " if ok else "ECHEC ") + f"{rel}/{f}", "" if ok else str(j.get("errors") or resp.status_code)[:200])
        bad += 0 if ok else 1
sys.exit(1 if bad else 0)
