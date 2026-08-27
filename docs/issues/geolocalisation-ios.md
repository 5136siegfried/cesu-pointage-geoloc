## 🐛 Géolocalisation refusée sur iPhone/Safari malgré l'autorisation du site

### Résumé

Sur iPhone (testé sur iPhone 15 Pro, Safari), la page de pointage servie directement par Apps Script (`Index.html` via `doGet`) s'ouvre correctement, mais `navigator.geolocation` renvoie systématiquement une erreur de type **refus de permission**, même après avoir explicitement autorisé la localisation pour le site dans **Réglages > Safari > Position**.

Sur PC, aucun souci d'ouverture constaté (non testé pour la géolocalisation à ce moment-là).

### Environnement

- Appareil : iPhone 15 Pro
- Navigateur : Safari (natif iOS)
- Interface concernée : page servie par `doGet` (Apps Script HtmlService)
- Réglages Safari : position autorisée pour le site

### Comportement attendu

Après autorisation de la localisation dans les réglages Safari, le clic sur "Pointer l'arrivée/départ" devrait déclencher la demande de position et l'enregistrer normalement.

### Comportement observé

Le pointage est bien enregistré (grâce à la gestion d'erreur déjà en place), mais avec le statut `À VÉRIFIER — position indisponible` et le détail `Localisation refusée ou désactivée sur le téléphone` — alors que la permission est bien accordée au niveau du site dans les réglages iOS.

### Cause identifiée

Les pages servies par Apps Script (`HtmlService`) tournent dans un **iframe sandboxé** imposé par Google (mode `IFRAME`, seul mode encore supporté — voir [documentation officielle](https://developers.google.com/apps-script/guides/html/restrictions)). La liste des attributs `sandbox` autorisés par cet iframe (`allow-same-origin`, `allow-forms`, `allow-scripts`, `allow-popups`, `allow-downloads`, `allow-modals`, `allow-popups-to-escape-sandbox`) **ne délègue pas la permission `geolocation`** au contenu de l'iframe.

Conséquence : Safari iOS applique la Permissions Policy au niveau de l'iframe imbriqué, indépendamment des réglages du site accordés au niveau du domaine de premier niveau. Le refus de géolocalisation est donc structurel à l'hébergement via `doGet`/`HtmlService`, pas un problème de configuration côté utilisateur.

Ce comportement est cohérent avec des retours similaires observés sur d'autres PWA/pages embarquées sous iOS récents (ex. [rapports de géolocalisation cassée pour des PWA sous iOS 26](https://developer.apple.com/forums/thread/804381)).

### Correctif appliqué

Ajout d'une interface externe (`docs/index.html`), hébergée hors du sandbox Apps Script via **GitHub Pages**. Cette page est un site statique classique, sans restriction de Permissions Policy héritée d'un iframe :

- La géolocalisation y fonctionne normalement (demande unique, mémorisée par le navigateur comme sur n'importe quel site).
- Elle communique avec le backend Apps Script exclusivement via un nouvel endpoint `doPost` (voir `Code.gs`), qui reste l'unique point d'écriture dans le Google Sheet.
- L'interface `Index.html` d'origine reste disponible mais n'est plus recommandée comme point d'entrée principal sur mobile.

### Action de suivi

- [x] Ajouter `doPost` au backend (`Code.gs`)
- [x] Créer `docs/index.html` comme interface externe
- [ ] Activer GitHub Pages sur le dépôt (Settings > Pages > branche `main`, dossier `/docs`)
- [ ] Renseigner `APPS_SCRIPT_URL` dans `docs/index.html`
- [ ] Régénérer le QR code utilisé sur le terrain avec l'URL GitHub Pages
- [ ] Valider sur iPhone que la géolocalisation fonctionne bien via la nouvelle page

### Références

- [Apps Script — HTML Service: Restrictions (sandbox IFRAME)](https://developers.google.com/apps-script/guides/html/restrictions)
- [Apple Developer Forums — geolocation denied in PWA under iOS 26](https://developer.apple.com/forums/thread/804381)