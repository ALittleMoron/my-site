FROM nginx:1.29.4-alpine

RUN rm -f /etc/nginx/conf.d/default.conf

COPY infra/nginx/nginx.conf /etc/nginx/nginx.conf
COPY infra/nginx/templates/ /etc/nginx/templates/
