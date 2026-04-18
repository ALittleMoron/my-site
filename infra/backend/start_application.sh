make migrate
make initbuckets
make collectstatic
make cli command="createsuperuser --username ${ADMIN_INIT_LOGIN} --password ${ADMIN_INIT_PASSWORD}"
make start_app
