# cesu-pointage-geoloc

Système de pointage géolocalisé simple pour particuliers employeurs (CESU), pensé pour l'aide à domicile.

Un salarié pointe son arrivée/départ en scannant un QR code sur place. La géolocalisation est capturée au moment du clic (pas de suivi continu), et l'horodatage est enregistré **côté serveur** — impossible à falsifier depuis le téléphone du salarié.

Fonctionne entièrement sur **Google Apps Script + Google Sheets** : gratuit, aucun hébergement à gérer.

## Fonctionnalités

- Page de pointage mobile (arrivée / départ)
- Sélection du salarié **et du client** — chaque client a ses propres coordonnées de référence
- Géolocalisation ponctuelle au moment du pointage
- Horodatage serveur (non modifiable côté client)
- Calcul automatique de la distance entre le pointage et l'adresse du client sélectionné
- Alerte automatique si le pointage a lieu hors zone (rayon configurable)
- Colonne "Vérifié par le manager" (case à cocher) dans le Google Sheet, pour que l'employeur valide chaque pointage
- Mention d'information RGPD/CNIL affichée directement dans l'application
- Crédit du projet open source et lien vers le dépôt

## ⚠️ Géolocalisation sur iPhone/Safari — pourquoi deux interfaces ?

Les pages servies directement par Apps Script (`Index.html`, via `doGet`) tournent dans un **iframe sandboxé** imposé par Google. Cet iframe ne délègue pas la permission de géolocalisation à son contenu : sur Safari iOS en particulier, `navigator.geolocation` est systématiquement refusé, **quels que soient les réglages du site dans Safari** — le blocage se fait au niveau de l'iframe, pas du site.

Pour contourner ce problème, le projet fournit une **deuxième interface**, `docs/index.html`, pensée pour être hébergée en dehors d'Apps Script via **GitHub Pages** (gratuit, directement depuis ce dépôt). Cette page est un site web normal, sans sandbox : la géolocalisation s'y comporte comme sur n'importe quel site (demande de permission une seule fois, mémorisée ensuite par le navigateur).

Cette page appelle Apps Script uniquement comme backend (`doPost`), qui reste le seul endroit où les données sont écrites dans le Sheet.

**C'est cette page (`docs/index.html`, hébergée sur GitHub Pages) qu'il faut utiliser pour le QR code**, pas l'URL `.../exec` d'Apps Script.

### Activer GitHub Pages

1. Dans les paramètres du dépôt GitHub : **Settings > Pages**.
2. Source : branche `main`, dossier `/docs`.
3. L'URL générée ressemble à `https://5136siegfried.github.io/cesu-pointage-geoloc/`.
4. Dans `docs/index.html`, remplacer `APPS_SCRIPT_URL` par l'URL de déploiement Apps Script (celle qui se termine par `/exec`).
5. Générer le QR code à partir de cette URL GitHub Pages, pas de l'URL Apps Script.

## Installation

1. Créer un Google Sheet vide.
2. Menu **Extensions > Apps Script**.
3. Coller `Code.gs` dans le fichier de script, créer un fichier HTML nommé `Index` et y coller `Index.html`.
4. Dans `Code.gs`, renseigner la liste `CLIENTS` (nom + latitude/longitude de chaque client) et la liste `SALARIEES`.
5. **Déployer > Nouveau déploiement > Application web** — exécuter en tant que "Moi", accès "Toute personne disposant du lien".
6. Générer un QR code pointant vers l'URL de déploiement, l'imprimer et le poser sur site.

## Gestion des erreurs

Le pointage n'est **jamais bloqué**, quelle que soit l'erreur rencontrée :

- **Localisation refusée, désactivée ou indisponible** → le pointage est quand même enregistré, avec le statut `À VÉRIFIER — position indisponible` et la raison précise dans la colonne "Détail erreur" (refus de permission, GPS indisponible, timeout...).
- **Échec de connexion au serveur** (pas de réseau, script indisponible) → rien n'est enregistré, un message d'erreur clair s'affiche avec un bouton **Réessayer**.
- **Erreur serveur inattendue** (Sheet verrouillé, quota dépassé...) → renvoyée proprement au client sans faire planter la page, avec bouton Réessayer.
- Les boutons de pointage sont désactivés pendant l'envoi pour éviter les doubles clics.

## Vérification par le manager

Chaque pointage crée une ligne dans l'onglet **Pointages** du Google Sheet, avec :
- l'horodatage serveur, le type (arrivée/départ), le salarié, le client
- la distance calculée par rapport au lieu attendu
- un statut (`OK` ou `À VÉRIFIER — hors zone`)
- une case à cocher **Vérifié par le manager**, à cocher une fois la ligne contrôlée

Les lignes se colorent automatiquement (rouge = à vérifier, vert = OK) grâce à une mise en forme conditionnelle créée dès le premier pointage.

Un onglet **"Tableau de bord"** est créé automatiquement en première position à l'ouverture de l'application. Il affiche en direct, sans aucune action manuelle :
- à gauche : les anomalies **non encore traitées** (statut à vérifier et case non cochée), triées de la plus récente à la plus ancienne
- à droite : les 20 derniers pointages, quel que soit leur statut

Dès qu'une ligne est cochée comme vérifiée dans l'onglet Pointages, elle disparaît automatiquement de la liste des anomalies du tableau de bord. Le manager n'a donc jamais besoin de faire défiler tout l'historique : le tableau de bord ne montre que ce qui reste à traiter.

## ⚠️ Avant utilisation — obligation légale (France)

La géolocalisation d'un salarié est encadrée par la CNIL, y compris pour un particulier employeur :

- **Informer explicitement le salarié** (avenant au contrat ou note écrite datée et signée) avant toute mise en place — la mention RGPD affichée dans l'application ne remplace pas cette formalité contractuelle.
- Ne capter la position **qu'au moment du pointage**, jamais en continu (ce projet respecte ce principe par conception).
- Proportionner l'usage au seul contrôle des horaires de présence.

Sans information préalable du salarié, la preuve issue de ce système pourrait être écartée en cas de litige prud'homal pour collecte déloyale. Ce projet ne constitue pas un conseil juridique — se rapprocher d'un professionnel du droit du travail en cas de doute.

## Licence

MIT — voir [LICENSE](./LICENSE).

## Auteur

Développé par [5136siegfried](https://github.com/5136siegfried) —
dépôt : [github.com/5136siegfried/cesu-pointage-geoloc](https://github.com/5136siegfried/cesu-pointage-geoloc)