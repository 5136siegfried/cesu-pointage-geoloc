# cesu-pointage-geoloc — version self-hosted

Application de pointage géolocalisé et de gestion CESU pour particuliers employeurs (aide à domicile), hébergée sur votre propre serveur — aucune dépendance à un service tiers.

## Fonctionnalités

- **Pointage géolocalisé** : arrivée/départ horodatés côté serveur, avec calcul automatique de la distance au client sélectionné et détection des pointages hors zone.
- **Gestion des employés** : fiches avec taux horaire, téléphone, numéro de sécurité sociale, date de naissance, adresse — informations utiles à la déclaration CESU (cesu.urssaf.fr).
- **Gestion des clients** : nom, prénom, coordonnées GPS (sélection sur carte Leaflet/OpenStreetMap, recherche d'adresse via Nominatim), conditions médicales, contact à prévenir, consignes propres à chaque client.
- **Planning récurrent** : créneaux par salariée/client/jour de semaine, avec comparatif automatique prévu/pointé sur la semaine en cours.
- **Tableau de bord** : heures et coût par salariée sur une période, export Excel (résumé + détail), correction manuelle d'un pointage en cas d'erreur avérée.
- **Bandeau d'alerte** : message piloté depuis l'admin, affiché sur la page de pointage.
- **PWA** : installable sur l'écran d'accueil, file d'attente locale en cas de coupure réseau.

## Architecture

Un seul conteneur Docker (Python + FastAPI + SQLite en fichier) — pas de base de données séparée, pas de dépendance Node.

```
selfhosted/
├── main.py              # routes FastAPI
├── db.py                # accès SQLite
├── calcul.py            # calcul heures/coût
├── planning.py           # comparatif planning vs pointages réels
├── config.py            # version, tolérance de distance
├── static/               # PWA (page de pointage, manifest, service worker, carte GPS)
├── templates/            # pages admin (Jinja2)
├── Dockerfile
├── docker-compose.yml
├── nginx-cesu-pointage.conf
├── deploy.sh             # mise à jour (git pull + rebuild)
└── backup.sh             # sauvegarde quotidienne du fichier SQLite
```

## Installation

### 1. Lancer le conteneur

```bash
docker compose up -d --build
```

Le conteneur écoute uniquement sur `127.0.0.1:8000` — un reverse proxy (nginx) est nécessaire pour l'exposer publiquement en HTTPS.

### 2. nginx + certbot

```bash
sudo cp nginx-cesu-pointage.conf /etc/nginx/sites-available/cesu-pointage
sudo nano /etc/nginx/sites-available/cesu-pointage   # adapter server_name à votre domaine
sudo ln -s /etc/nginx/sites-available/cesu-pointage /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d votre-domaine.fr
```

### 3. Protéger /admin

```bash
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd-cesu manager
```

Aucun identifiant n'est codé dans l'application : l'accès à `/admin` est protégé exclusivement par nginx (Basic Auth). Choisissez votre propre mot de passe à cette étape.

### 4. Sauvegarde automatique

```bash
crontab -e
# ajouter :
0 3 * * * /chemin/vers/cesu-pointage-geoloc/selfhosted/backup.sh >> /var/log/cesu-backup.log 2>&1
```

Sauvegarde quotidienne du fichier SQLite, conservée 30 jours glissants.

## Mise à jour

```bash
./deploy.sh
```

Fait `git pull` + rebuild + nettoyage des anciennes images en une commande.

## Premier lancement

Les tables employés et clients sont pré-remplies avec des valeurs d'exemple à la première exécution. Modifiez-les depuis `/admin/employes` et `/admin/clients`, ou supprimez-les si elles ne correspondent à rien de réel.

## Sécurité et confidentialité

- Toutes les données (pointages, employés, clients, y compris conditions médicales et numéro de sécurité sociale) sont stockées localement, dans un unique fichier SQLite (`data/pointages.db`). Aucune donnée ne transite vers un service tiers.
- La page `/consignes?client=...` (consignes, conditions médicales, contact d'urgence) est accessible sans authentification, volontairement — l'aide à domicile doit pouvoir la consulter sur le terrain sans se connecter à l'admin. Ces informations ne sont donc protégées que par la confidentialité de l'URL de l'application.
- `/admin` est protégé par Basic Auth au niveau de nginx — rien n'est codé en dur côté application.
- La correction manuelle d'un pointage (`/admin/pointage/{id}`) écrase la valeur d'origine sans conserver d'historique des modifications.

## Obligation légale (géolocalisation d'un salarié, France)

La géolocalisation d'un salarié est encadrée par la CNIL, y compris pour un particulier employeur :

- **Informer explicitement le salarié** (avenant au contrat ou note écrite datée et signée) avant toute mise en place — la mention RGPD affichée dans l'application ne remplace pas cette formalité contractuelle.
- Ne capter la position **qu'au moment du pointage**, jamais en continu (l'application respecte ce principe par conception).
- Proportionner l'usage au seul contrôle des horaires de présence.

Ce projet ne constitue pas un conseil juridique — se rapprocher d'un professionnel du droit du travail en cas de doute.

## Ce que cet outil ne fait pas

- Il ne remplace pas la **déclaration CESU officielle** (cotisations, bulletin de paie, prélèvement), qui se fait sur cesu.urssaf.fr. Cet outil prépare les chiffres (heures réelles, coût estimé) à reporter là-bas.
- Pas de gestion des congés payés ni de vue annuelle consolidée à ce jour.

## Licence

MIT — voir [LICENSE](./LICENSE).

## Auteur

[5136siegfried](https://github.com/5136siegfried) — [github.com/5136siegfried/cesu-pointage-geoloc](https://github.com/5136siegfried/cesu-pointage-geoloc)
