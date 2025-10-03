make migrate
make litestar command="initbuckets"
make litestar command="collectstatic"
make litestar command="createsuperuser --username ${ADMIN_INIT_LOGIN} --password ${ADMIN_INIT_PASSWORD}"
make start_app
