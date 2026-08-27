# cesu-pointage-geoloc

Système de pointage géolocalisé simple pour particuliers employeurs (CESU), pensé pour l'aide à domicile.

Un salarié pointe son arrivée/départ en scannant un QR code sur place. La géolocalisation est capturée au moment du clic (pas de suivi continu), et l'horodatage est enregistré **côté serveur** — impossible à falsifier depuis le téléphone du salarié.

Fonctionne entièrement sur **Google Apps Script + Google Sheets** : gratuit, aucun hébergement à gérer.

## Fonctionnalités

- Page de pointage mobile (arrivée / départ) avec sélection du salarié
- Géolocalisation ponctuelle au moment du pointage
- Horodatage serveur (non modifiable côté client)
- Calcul automatique de la distance entre le pointage et l'adresse de référence
- Alerte automatique si le pointage a lieu hors zone (rayon configurable)
- Historique complet dans un Google Sheet, exploitable pour la paie

## Installation

1. Créer un Google Sheet vide.
2. Menu **Extensions > Apps Script**.
3. Coller `Code.gs` dans le fichier de script, créer un fichier HTML nommé `Index` et y coller `Index.html`.
4. Dans `Code.gs`, renseigner `DOMICILE_LAT`, `DOMICILE_LNG` (coordonnées du lieu à pointer) et la liste `SALARIEES`.
5. **Déployer > Nouveau déploiement > Application web** — exécuter en tant que "Moi", accès "Toute personne disposant du lien".
6. Générer un QR code pointant vers l'URL de déploiement, l'imprimer et le poser sur site.

## ⚠️ Avant utilisation — obligation légale (France)

La géolocalisation d'un salarié est encadrée par la CNIL, y compris pour un particulier employeur :

- **Informer explicitement le salarié** (avenant au contrat ou note écrite datée et signée) avant toute mise en place.
- Ne capter la position **qu'au moment du pointage**, jamais en continu (ce projet respecte ce principe par conception).
- Proportionner l'usage au seul contrôle des horaires de présence.

Sans information préalable du salarié, la preuve issue de ce système pourrait être écartée en cas de litige prud'homal pour collecte déloyale. Ce projet ne constitue pas un conseil juridique — se rapprocher d'un professionnel du droit du travail en cas de doute.

## Licence

MIT — voir [LICENSE](./LICENSE).
