
Instalando as dependencias do python:

- pip install -r services/common/requirements.txt

Rodando localmente os services:

- npm install -g serverless
- npm install serverless-offline
- serverless offline start

Rodar o banco de dados:

- make up
- make restore (caso precise criar as tabelas e popular o banco de dados)


Obervação: Caso deseje importar os requests no seu Insomnia, só utilizar o arquivo microservices-guacaloka.json


# 📦 Microserviços - E-commerce GuacaLoka

Este projeto contém os endpoints principais dos microserviços da API do sistema de e-commerce GuacaLoka. Abaixo está a documentação de cada rota, seu propósito, método, payloads esperados e exemplos de resposta.

## 🔐 Autenticação

### `POST /dev/auth`

Autentica o usuário e retorna um token JWT.

**Requisição:**

```json
{
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

**Resposta:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 👤 Cadastro de Cliente

### `POST /dev/customers`

Cria um novo cliente na plataforma.

**Requisição:**

```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

---

## 📦 Produtos

### `POST /dev/products`

Retorna a lista de produtos associados a um pedido.

**Requisição:**

```json
{
  "id_pedido": 123
}
```

**Resposta:**

```json
[
  {
    "product_id": 9,
    "name": "Pimentinha",
    "price": 3.9,
    "description": "Uma explosão de sabor em formato mini! Ideal pra quem gosta de fogo na boca.",
    "category": {
      "id": 12,
      "name": "Clássico"
    }
  }
]
```

---

## 🛒 Carrinho

### `GET /dev/cart`

Retorna os itens atuais do carrinho do usuário.

**Resposta:**

```json
{
  "id": "1",
  "items": [...],
  "total": 53.8,
  "total_count": 1
}
```

---

### `POST /dev/cart/add_item`

Adiciona um item ao carrinho.

**Requisição:**

```json
{
  "product_id": "47",
  "quantity": 2
}
```

**Resposta:**

```json
{
  "message": "Item added to cart successfully",
  "cart_item": {
    "product_id": "47",
    "quantity": 2
  }
}
```

---

### `DELETE /dev/cart/remove_item/{item_id}`

Remove um item específico do carrinho.

**Exemplo:**

`DELETE /dev/cart/remove_item/10`

**Resposta:**

```json
{
  "message": "Item removed from cart successfully"
}
```

---

## 🧾 Pedidos

### `GET /dev/orders`

Retorna a lista de pedidos do usuário.

**Resposta:**

```json
[
  {
    "id": 7,
    "created_at": "07/05/2025",
    "status": "NO CARRINHO",
    "total": 53.8
  }
]
```

---

## 🚚 Frete

### `POST /dev/shipping`

Calcula o frete com base no CEP informado.

**Requisição:**

```json
{
  "cep": "57100000"
}
```

**Resposta:**

```json
{
  "cep": "57100-000",
  "localidade": "Rio Largo",
  "uf": "AL",
  "frete": 12.323
}
```

---

## 💳 Checkout

### `POST /dev/checkout`

Finaliza o pedido atual com o método de pagamento informado.

**Requisição:**

```json
{
  "payment_method": "credit_card"
}
```

**Resposta:**

```json
{
  "message": "Order placed successfully",
  "order": {
    "order_id": 5,
    "status": "confirmed",
    "payment_method": "credit_card",
    "items": [...],
    "total": 53.8
  }
}
```

---

## 🤖 Recomendador de Produtos

### `GET /dev/product_suggestor`

Retorna sugestões de produtos baseadas no histórico de compras ou preferências.

**Resposta:**

```json
{
  "recommended_products": [
    "Burrito",
    "Combo Nachos + Guacamole"
  ]
}
```