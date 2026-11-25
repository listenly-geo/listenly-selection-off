# Sélection quotidienne des fiches moment (copie de travail)

Scripts : automation/scripts/moteur_autonome_moments.py, enrichir_du_jour.py, indexation_du_jour.py (et moment_urls.py).
Données : pages/podcast-btb/data, automation/moments_connus, automation/inbox, data/gsc, automation/marketforge_engine/trafic_seo.json.

Ordre d'exécution depuis la racine du dépôt :
1. python3 automation/scripts/moteur_autonome_moments.py
2. python3 automation/scripts/enrichir_du_jour.py   (nécessite ANTHROPIC_API_KEY)
3. python3 automation/scripts/moteur_autonome_moments.py
4. python3 automation/scripts/indexation_du_jour.py   (nécessite GSC_SERVICE_ACCOUNT_JSON et ANTHROPIC_API_KEY)

Résultat : pages/podcast-btb/data/indexation_du_jour.json (liste des 10 fiches du jour).
Les clés ne sont jamais écrites dans ce dépôt.
