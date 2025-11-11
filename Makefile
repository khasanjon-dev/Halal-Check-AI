build:
	docker compose up --build
down:
	docker compose down
down_v:
	docker compose down -v
restart:
	make down_v && make build