# Moteur trafic Listenly : sélection du jour, indexation, tableau de suivi

Dépôt : `listenly-geo/listenly-selection-off` (public, branche `main`). C'est LE dépôt de travail du système de sélection.
L'ancien dépôt `listenly-geo/listenlygeo` (moteur de prospection MarketForge + ancien moteur trafic) est déconnecté de Claude (erreur 403) : ne pas s'en servir, ne rien y pousser.

## Qui / pourquoi
Etienne (français, fondateur de Listenly et MarketForge). Objectif unique : 10 K€/mois de ventes de l'Index. Ce système apporte du trafic Google vers listenly.org en faisant indexer chaque jour 10 pages de « moments » (une question + la réponse extraite d'un épisode de podcast). Répondre en français, listes courtes, langage simple, expliquer dans le chat AVANT d'agir avec des outils, donner les liens exacts quand une action manuelle est demandée.

## Règles à respecter
- Ne JAMAIS écrire de clé, jeton ou mot de passe dans un fichier ou dans le chat. Etienne ajoute lui-même ses secrets dans GitHub (jamais lui demander de les coller dans le chat).
- Ne rien envoyer à Google (demande d'indexation) et ne rien publier sans sa validation dans le chat.
- Ne pas créer d'autre dépôt ni copier le moteur ailleurs sans son accord.
- Fiches exclues définitivement : `pages/podcast-btb/data/fiches_exclues.json` (ne plus en parler, ne plus les proposer).
- Messages de commit terminés par les lignes de co-auteur et de session demandées par l'environnement.

## Vocabulaire
- Moment : clé `podcast/code` (ex. `msp-unplugged/31f896ead2`). Adresse ancienne : `https://listenly.org/podcast-btb/m/<podcast>/<10hex>`. Adresse par question (préférée) : `.../m/<podcast>/<question-slug>` (table `pages/podcast-btb/data/slugs_moments.json`, outil `automation/scripts/moment_urls.py`).
- 404 = fiche absente du serveur. Page 200 + `noindex` = existe mais trop mince ; devient indexable après « rallonge » de la réponse ET déploiement des données sur le serveur.
- Titre SEO : la question raccourcie, gardée interrogative (≤ 58 caractères avec le suffixe « | Podcast »), stockée dans `data/titres_seo.json`.

## Fonctionnement quotidien (cible : liste prête à 8h00 Berlin, tous les jours)
Workflow `.github/workflows/selection-du-jour.yml` (id 430245379) :
1. `moteur_autonome_moments.py` note les moments candidats.
2. `enrichir_du_jour.py` rallonge les réponses (clé ANTHROPIC_API_KEY). Échoue souvent faute de transcriptions dans ce dépôt (« transcription insuffisante »).
3. `indexation_du_jour.py` choisit 10 fiches (fiches déjà en ligne d'abord, jamais déjà demandées, répartition connu/mot-clé, max 3 par podcast).
   - Contrôle titre/question (27/11/2026) : `titre_coherent()` écarte un titre dérivé ou trop court ; essai d'un titre régénéré, sinon fiche écartée (`ecartees_sens_recherche` dans le JSON).
   - Archivage automatique (27/11/2026) : avant d'écraser la liste, celle de la veille est ajoutée à `index_requests.json` (statut « En cours » puis « Indexé » via Search Console). Plus aucune saisie manuelle.
4. Commit/push du résultat : `pages/podcast-btb/data/indexation_du_jour.json` (champ `urls`, avec `score_qualite`, `titre`, `http`).
Déclencheurs : crons `17 5`, `8 6`, `41 6`, `13 7`, `37 7` (UTC), plus une garde qui saute si la liste du jour existe déjà. PROBLÈME CONNU : GitHub lance les crons avec ~10 h de retard (vers 17-18h UTC). Relance manuelle fiable :
`gh api -X POST repos/listenly-geo/listenly-selection-off/actions/workflows/430245379/dispatches -f ref=main` (puis attendre 2-4 min). Une tâche planifiée Claude (8h Berlin) est la solution visée ; elle doit être créée depuis une conversation qui n'a QUE ce dépôt (sinon refus « accès à un dépôt refusé »).

## Rapport du matin à envoyer à Etienne (en français)
Date, nombre de fiches prêtes, puis pour chaque fiche : numéro, question traduite, titre court traduit, podcast, note sur 10 (= score_qualite / 10), lien ; fiches écartées ; échecs. Finir par « Je lance la vague d'indexation dans Search Console ? ».

## Vague d'indexation (faite avec Claude in Chrome, après son accord)
Propriété Search Console : `sc-domain:listenly.org`. Pour chaque URL : ouvrir https://search.google.com/search-console?resource_id=sc-domain%3Alistenly.org, cliquer la barre « Inspecter n'importe quelle URL », coller l'URL, Entrée, puis « Demander une indexation », attendre ~60 s jusqu'à « Indexation demandée », « Masquer ». S'arrêter à « Quota dépassé ». Fermer l'onglet. Ensuite enregistrer la vague dans `index_requests.json` (clé `AAAA-MM-JJ`, `urls_demandees`), lancer `sync_suivi_fiches.py` + `build_suivi_vues.py`, commit, push. Les liens directs `inspect?...&id=` ne marchent pas (404).

## Tableau de suivi (mise à jour automatique)
- Page : `pages/podcast-btb/suivi-indexation-7hQ2xK9pL4mW.html`, publiée sur GitHub Pages : https://listenly-geo.github.io/listenly-selection-off/ (non joignable depuis l'environnement Claude : proxy).
- Onglets : Réservoir (fiches ajoutées par le moteur, `reservoir_questions.json` + `reservoir_base.json`), En cours (10 du jour + demandées non indexées), Indexé (confirmé par Search Console).
- Workflow `suivi-tableau.yml` (id 430262860) : se déclenche après la sélection, à chaque modif de `index_requests.json`, ou à la main. Étapes : `gsc_pull.py` (secret GSC_SERVICE_ACCOUNT_JSON, compte `gsc-lecture@listenlylegacy.iam.gserviceaccount.com`), `sync_suivi_fiches.py`, `build_suivi_vues.py`, publication Pages. Envoi FTP vers listenly.org en échec depuis GitHub (canal de données coupé) ; repli prêt via cPanel (`deploy_tableau_cpanel.py`, secrets CPANEL_USER/CPANEL_TOKEN non posés).
- Secrets en place (noms) : ANTHROPIC_API_KEY, GSC_SERVICE_ACCOUNT_JSON, (FTP_*).

## Points ouverts
1. Déclencheur quotidien fiable à 8h (tâche planifiée Claude depuis une conversation sans l'ancien dépôt).
2. Déploiement des données vers listenly.org (adresses par question, titres SEO, fiches rallongées) : nécessite CPANEL_USER et CPANEL_TOKEN.
3. Enrichissement : transcriptions manquantes dans ce dépôt.
4. Réservoir figé au 24/11 : le moteur qui l'alimente est dans l'ancien dépôt.
5. Heure d'été (fin mars) : décaler les crons d'une heure vers le bas.
