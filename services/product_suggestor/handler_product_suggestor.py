import psycopg2
import os
import sys
import json
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token

def encode_purchase_history(user_purchase_history, all_products):
    encoded_history = np.zeros(len(all_products))
    for product in user_purchase_history:
        if product in all_products:
            encoded_history[all_products.index(product)] = 1
    return encoded_history

def create_neural_network(input_size, hidden_size, output_size):
    np.random.seed(0)
    W1 = np.random.randn(input_size, hidden_size)
    b1 = np.zeros(hidden_size)
    W2 = np.random.randn(hidden_size, output_size)
    b2 = np.zeros(output_size)
    return W1, b1, W2, b2

def relu(x):
    return np.maximum(0, x)

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def forward_propagation(X, W1, b1, W2, b2):
    Z1 = np.dot(X, W1) + b1
    A1 = relu(Z1)
    Z2 = np.dot(A1, W2) + b2
    A2 = sigmoid(Z2)
    return A2

def recommend_products(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT p.name
            FROM order_items oi
            JOIN product p ON p.id_product = oi.product_id
            JOIN orders o ON o.id = oi.order_id
            WHERE o.customer_id = %s;
        """, (user_id,))
        user_purchase_history = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT p.name, c.name
            FROM product p
            LEFT JOIN category c ON c.id = p.category_id;
        """)

        product_data = cursor.fetchall()
        
        all_products = [data[0] for data in product_data] 
        product_categories = {data[0]: data[1] for data in product_data}

        encoded_history = encode_purchase_history(user_purchase_history, all_products)
        
        input_size = len(encoded_history)
        hidden_size = 10 
        output_size = len(all_products)
        
        W1, b1, W2, b2 = create_neural_network(input_size, hidden_size, output_size)
        
        recommendations_encoded = forward_propagation(encoded_history, W1, b1, W2, b2)
        
        recommendations = [
            all_products[i] for i in range(len(all_products))
            if recommendations_encoded[i] > 0.5 and all_products[i] not in user_purchase_history
        ]
        
        cursor.execute("""
            SELECT DISTINCT ON (p.name) 
                p.name, p.description, p.price, p.picture_url
            FROM product p
            WHERE p.name = ANY(%s);
        """, (recommendations,))
        recommended_product_rows = cursor.fetchall()

        cursor.execute("""
            DELETE FROM product
            WHERE category_id = 15;
        """)

        for name, description, price, picture_url in recommended_product_rows:
            cursor.execute("""
                INSERT INTO product (name, description, price, category_id, picture_url)
                VALUES (%s, %s, %s, %s, %s);
            """, (name, description, price, 15, picture_url))

        conn.commit()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'recommended_products': recommendations
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    finally:
        cursor.close()
        conn.close()

def handler(event, context):
    token = event['headers'].get('Authorization', '').replace('Bearer ', '')
    user_data = validate_token(token)
    
    if not user_data:
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Unauthorized'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    user_id = user_data['sub']
    return recommend_products(user_id)
