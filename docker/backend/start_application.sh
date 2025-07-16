make migrate
make litestar command="initbuckets"
make litestar command="collectstatic"
make litestar command="createsuperuser --username ${INIT_ADMIN_LOGIN} --password ${INIT_ADMIN_PASSWORD}"
make start_app
