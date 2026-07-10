FROM nginxinc/nginx-unprivileged:1.31.2-alpine

USER root

RUN apk add --no-cache --upgrade c-ares=1.34.8-r0 \
 && rm -f /etc/nginx/conf.d/default.conf

COPY --chown=nginx:nginx infra/nginx/nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx infra/nginx/templates/ /etc/nginx/runtime-templates/

USER nginx
