#!/bin/bash
set -e

# Use a directory where odoo user has permissions
CUSTOM_DIR=/var/lib/odoo/custom_addons
FILESTORE_DIR=/var/lib/odoo/filestore

if [[ -z "$CUSTOM_MODULES_BUCKET" ]]; then
  echo "ERROR: CUSTOM_MODULES_BUCKET not set"
  exit 1
fi

if [[ -z "$FILESTORE_BUCKET" ]]; then
  echo "WARNING: FILESTORE_BUCKET not set, filestore data will not persist between container restarts"
else
  echo "Syncing filestore data from gs://$FILESTORE_BUCKET → $FILESTORE_DIR"
  gsutil -m rsync -r gs://$FILESTORE_BUCKET $FILESTORE_DIR || echo "Failed to sync filestore data, but continuing..."
fi

echo "Syncing custom modules from gs://$CUSTOM_MODULES_BUCKET → $CUSTOM_DIR"
gsutil -m rsync -r gs://$CUSTOM_MODULES_BUCKET $CUSTOM_DIR || echo "Failed to sync custom modules, but continuing..."

# Start Odoo with configuration file and database settings from environment
exec odoo -c /etc/odoo/odoo.conf \
  --db_host="$DB_HOST" \
  --db_port="$DB_PORT" \
  --db_user="$DB_USER" \
  --db_password="$DB_PASSWORD" \
  --http-port="$PORT" \
  --http-interface=0.0.0.0
