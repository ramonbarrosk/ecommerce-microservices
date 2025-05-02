# Sobe o container
up:
	docker-compose up -d

# Executa o dump.sql dentro do container
restore:
	docker cp dump.sql postgres_db:/tmp/dump.sql
	docker exec -it postgres_db psql -U user -d ecommerce_db -f /tmp/dump.sql

# Derruba os containers
down:
	docker-compose down
