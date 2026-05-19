#!/bin/sh
set -e

if [ -f /usr/share/nginx/html/sitemap.xml ]; then
  envsubst '${APP_DOMAIN}' < /usr/share/nginx/html/sitemap.xml > /tmp/sitemap.xml \
    && mv /tmp/sitemap.xml /usr/share/nginx/html/sitemap.xml
fi
