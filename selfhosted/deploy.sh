#!/usr/bin/env bash
# Script de mise à jour — à lancer sur le VPS, dans le dossier selfhosted/.
# Usage : ./deploy.sh

set -euo pipefail

echo "→ Récupération de la dernière version..."
git pull

echo "→ Reconstruction et redémarrage du conteneur..."
docker compose up -d --build

echo "→ Nettoyage des anciennes images inutilisées..."
docker image prune -f

echo "✅ Déployé. Logs en direct : docker compose logs -f cesu-pointage"
