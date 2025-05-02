Microservices Ecommerce

Instalando as dependencias do python:

- pip install -r services/common/requirements.txt

Rodando localmente os services:

- npm install -g serverless
- npm install serverless-offline
- serverless offline start

Rodar o banco de dados:

- make up
- make restore (caso precise criar as tabelas e popular o banco de dados)
