# Changelog

## 1.5.0
- Documentation et changelog accessibles depuis l'admin
- Tutoriel de première installation (ajout à l'écran d'accueil) en bas de la page de pointage

## 1.4.0
- Détection des séquences Arrivée/Départ incohérentes (confirmation en amont + anomalie remontée au tableau de bord)
- Labels explicites et récapitulatif salariée/client sur la page de pointage
- Carte de vérification GPS sur la fiche pointage (position capturée vs position attendue)
- Bandeau de version, fiches employés enrichies pour la CESU (téléphone, n° sécu, date de naissance, adresse)
- Design admin partagé et responsive (static/admin.css)

## 1.3.0
- Gestion des clients (sites) depuis l'admin : fiche complète (conditions médicales, contact d'urgence, consignes propres au client)
- Sélection GPS sur carte Leaflet/OpenStreetMap avec recherche d'adresse (Nominatim), sans clé API

## 1.2.0
- Planning récurrent par salariée/client/jour, avec comparatif prévu vs réel sur la semaine en cours
- Correction manuelle d'un pointage depuis l'admin

## 1.1.0
- Gestion des employés depuis l'admin (taux horaire, actif/inactif)
- Tableau de bord : heures et coût par période, export Excel
- Bandeau d'alerte et consignes pour les salariées

## 1.0.0
- Version self-hosted initiale : pointage géolocalisé, horodatage serveur
- Gestion des erreurs (géolocalisation refusée, coupure réseau) sans jamais bloquer le pointage
- PWA installable, file d'attente locale hors-ligne
