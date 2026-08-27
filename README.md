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

## Installation

1. Créer un Google Sheet vide.
2. Menu **Extensions > Apps Script**.
3. Coller `Code.gs` dans le fichier de script, créer un fichier HTML nommé `Index` et y coller `Index.html`.
4. Dans `Code.gs`, renseigner la liste `CLIENTS` (nom + latitude/longitude de chaque client) et la liste `SALARIEES`.
5. **Déployer > Nouveau déploiement > Application web** — exécuter en tant que "Moi", accès "Toute personne disposant du lien".
6. Générer un QR code pointant vers l'URL de déploiement, l'imprimer et le poser sur site.

## Vérification par le manager

Chaque pointage crée une ligne dans l'onglet **Pointages** du Google Sheet, avec :
- l'horodatage serveur, le type (arrivée/départ), le salarié, le client
- la distance calculée par rapport au lieu attendu
- un statut (`OK` ou `À VÉRIFIER — hors zone`)
- une case à cocher **Vérifié par le manager**, à cocher une fois la ligne contrôlée

Aucune interface séparée n'est nécessaire : le manager (l'employeur) travaille directement dans le Sheet.

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