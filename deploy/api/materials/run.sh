#!/bin/sh
SCRIPT_DIR=$(cd $(dirname "$0"); pwd)
TRANSFER_ROOT=/data/transfer
export STATIC_ROOT=/data/static/app/
export EXPORT_ROOT=/data/export/app/
export UPLOAD_ROOT=/data/upload/app/
export LOG_ROOT=/var/log/app/
cd ${SCRIPT_DIR}
sed -i 's|processes = 8|processes = '${PROCESSES}'|g' ${SCRIPT_DIR}/uwsgi.ini
sed -i 's|service_name|'${SERVICE_NAME}'|g' /etc/nginx/sites-enabled/default
service nginx start
#uwsgi --ini ${SCRIPT_DIR}/uwsgi.ini
python3 manage.py runserver 127.0.0.1:8080
