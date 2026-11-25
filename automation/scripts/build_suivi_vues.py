"""Alimente le tableau de suivi (24/11/2026, decision d'Etienne) :
- RESERVOIR : toutes les fiches/questions des leur creation par le moteur (reservoir_questions.json),
  plus la base historique (reservoir_base.json), les plus recentes en premier ;
- EN COURS : les fiches du jour selectionnees (indexation_du_jour.json), avant meme la demande d'indexation.
Sortie : pages/podcast-btb/data/suivi_vues.json (lu par le tableau)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import moment_urls as mu
D = "pages/podcast-btb/data"
def jl(p, d):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return d
norm = lambda t: re.sub(r"\W+", " ", (t or "").lower()).strip()
titres = jl(f"{D}/titres_seo.json", {}).get("titres", {})
jour = jl(f"{D}/indexation_du_jour.json", {})
req = jl(f"{D}/index_requests.json", {})
suivi = jl(f"{D}/suivi_fiches.json", {}).get("fiches", [])
statut = jl(f"{D}/statut_indexation.json", {}).get("pages", {})

def info(u):
    k = mu.path_to_key(u) or ""
    if "/" not in k: return "", ""
    slug, mid = k.split("/")
    try:
        e = json.load(open(f"{D}/moments/{slug}.json", encoding="utf-8"))
        return e["entries"][mid].get("q", ""), e.get("podcast") or slug.replace("-", " ").title()
    except Exception:
        return "", slug.replace("-", " ").title()

# fiches deja suivies : elles quittent le Reservoir
demandees = {u for e in req.values() if isinstance(e, dict) for u in e.get("urls_demandees", [])} | {f["url"] for f in suivi} | set(statut)
du_jour, jours = [], set()
for x in jour.get("urls", []):
    u = x["url"]; q, p = info(u)
    k = mu.path_to_key(u) or ""
    du_jour.append({"date": jour.get("date", ""), "url": u, "podcast": p,
                    "question": titres.get(k) or x.get("titre") or q})
    jours.add(u)
    if q: demandees.add(u)
vus = {norm(f["question"]) for f in du_jour} | {norm(q) for q in (info(u)[0] for u in demandees) if q}

res, seen = [], set()
def add(r):
    n = norm(r["question"])
    if not n or n in seen or r.get("url") in demandees or r.get("url") in jours or n in vus: return
    seen.add(n); res.append(r)
for i in jl("automation/marketforge_engine/reservoir_questions.json", {}).get("items", []):
    add({"date": i.get("date_ajout", ""), "question": i.get("question", ""),
         "podcast": i.get("podcast_name") or i.get("podcast_slug", "").replace("-", " ").title(),
         "url": i.get("fiche_url") or i.get("n1_url", ""), "indexation": "À traiter"})
for r in jl(f"{D}/reservoir_base.json", []):
    add(r)
res.sort(key=lambda r: r.get("date") or "", reverse=True)
json.dump({"date": jour.get("date", ""), "du_jour": du_jour, "reservoir": res}, open(f"{D}/suivi_vues.json", "w", encoding="utf-8"), ensure_ascii=False)
print("du_jour:", len(du_jour), "reservoir:", len(res), "recent:", res[0]["date"] if res else "-")
