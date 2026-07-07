FROM nginxinc/nginx-unprivileged:1.31.2-alpine

RUN rm -f /etc/nginx/conf.d/default.conf

COPY --chown=nginx:nginx infra/nginx/nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx infra/nginx/templates/ /etc/nginx/runtime-templates/

USER nginx
