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

    user_id = user_data['sub']

    try:
        cursor.execute("""
            SELECT 
                o.id AS id,
                p.name AS product_name,
                p.description AS product_description,
                oi.quantity,
                oi.price_at_purchase,
                oi.id AS item_id
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            JOIN product p ON p.id_product = oi.product_id
            WHERE o.customer_id = %s AND o.status =  %s
            ORDER BY o.created_at DESC;
        """, (user_id, 'pending'))

        rows = cursor.fetchall()

        cart_details = {
            'id': f"{user_id}",
            'items': []
        }

        total_items_cart = 0

        for row in rows:
            cart_details['items'].append({
                'product_name': row[1],
                'product_description': row[2],
                'quantity': row[3],
                'price_at_purchase': float(row[4]),
                'item_id': row[5]
            })
        
        total_items_cart = len(cart_details['items'])

        total_pedido = sum(item['quantity'] * item['price_at_purchase'] for item in cart_details['items'])
        cart_details['total'] = total_pedido
        cart_details['total_count'] = total_items_cart


        return {
            'statusCode': 200,
            'body': json.dumps(cart_details),
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