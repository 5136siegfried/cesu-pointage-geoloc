#!/usr/bin/env bash
# Sauvegarde quotidienne du fichier SQLite — à brancher sur une tâche cron.
# Exemple crontab (tous les jours à 3h du matin) :
#   0 3 * * * /opt/cesu-pointage-geoloc/selfhosted/backup.sh >> /var/log/cesu-backup.log 2>&1

set -euo pipefail

SOURCE_DB="$(dirname "$0")/data/pointages.db"
BACKUP_DIR="$(dirname "$0")/backups"
RETENTION_JOURS=30

mkdir -p "$BACKUP_DIR"

if [ ! -f "$SOURCE_DB" ]; then
  echo "❌ Fichier introuvable : $SOURCE_DB"
  exit 1
fi

DATE=$(date +%F)
cp "$SOURCE_DB" "$BACKUP_DIR/pointages-$DATE.db"
echo "✅ Sauvegarde créée : $BACKUP_DIR/pointages-$DATE.db"

# Supprime les sauvegardes de plus de $RETENTION_JOURS jours
find "$BACKUP_DIR" -name "pointages-*.db" -mtime +"$RETENTION_JOURS" -delete
