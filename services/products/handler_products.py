import psycopg2
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token

def handler(event, context):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT product.name, price, description, 
                category.id AS category_id, 
                category.name AS category_name, product.id_product AS product_id
            FROM product 
            LEFT JOIN category ON category.id = product.category_id
        """)

        products = cursor.fetchall()

        product_list = [
            {   
                'product_id': product_id,
                'name': name, 
                'price': float(price), 
                'picture_url': "https://m.media-amazon.com/images/I/71MPpz9jw9L._AC_SX679_.jpg",
                'description': description, 
                'category': {
                    'id': category_id, 
                    'name': category_name
                }
            } 
            for name, price, description, category_id, category_name, product_id in products
        ]

        return {
            'statusCode': 200,
            'body': json.dumps(product_list),
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