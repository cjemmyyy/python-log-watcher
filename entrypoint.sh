#!/bin/sh

mkdir -p /var/log/nginx

rm -f /var/log/nginx/access.log /var/log/nginx/error.log
touch /var/log/nginx/access.log /var/log/nginx/error.log
chown -R nginx:nginx /var/log/nginx || true

envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

nginx -g 'daemon off;'