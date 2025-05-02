import psycopg2
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token

def handler(event, context):
    token = event['headers'].get('Authorization', '').replace('Bearer ', '')

    user_data = validate_token(token)
    if not user_data:
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Unauthorized'})
        }

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT product.name, price, description, 
                category.id AS category_id, 
                category.name AS category_name 
            FROM product 
            LEFT JOIN category ON category.id = product.category_id
        """)

        products = cursor.fetchall()

        product_list = [
            {
                'name': name, 
                'price': float(price), 
                'description': description, 
                'category': {
                    'id': category_id, 
                    'name': category_name
                }
            } 
            for name, price, description, category_id, category_name in products
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