import psycopg2
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token


def get_order(order_id, user_id, cursor):
    try:
        cursor.execute("""
            SELECT 
                o.id AS id,
                TO_CHAR(o.created_at, 'DD/MM/YYYY') AS data_criacao,
                CASE 
                    WHEN o.status = 'pending' THEN 'NO CARRINHO'
                    WHEN o.status = 'done' THEN 'FINALIZADO'
                    ELSE o.status
                END AS status,
                oi.quantity,
                oi.price_at_purchase,
                p.name AS product_name,
                p.description AS product_description
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            JOIN product p ON p.id_product = oi.product_id
            WHERE o.customer_id = %s AND o.id = %s
            ORDER BY o.created_at DESC;
        """, (user_id, order_id))

        rows = cursor.fetchall()

        if not rows:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Order not found'}),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
        
        order_details = {
            'id': rows[0][0],
            'created_at': rows[0][1],
            'status': rows[0][2],
            'items': []
        }

        for row in rows:
            order_details['items'].append({
                'product_name': row[5],
                'product_description': row[6],
                'quantity': row[3],
                'price_at_purchase': float(row[4]),
            })

        total_pedido = sum(item['quantity'] * item['price_at_purchase'] for item in order_details['items'])
        order_details['total'] = total_pedido

        return {
            'statusCode': 200,
            'body': json.dumps(order_details),
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
    path_parameters = event.get('pathParameters', None)
    if path_parameters is not None:
        order_id = path_parameters.get('id')
    else:
        order_id = None

    if order_id:
        return get_order(order_id, user_id, cursor)

    try:
        cursor.execute("""
            SELECT 
                o.id AS id,
                TO_CHAR(o.created_at, 'DD/MM/YYYY') AS data_criacao,
                CASE 
                    WHEN o.status = 'pending' THEN 'NO CARRINHO'
                    WHEN o.status = 'done' THEN 'FINALIZADO'
                    ELSE o.status
                END AS status,
                SUM(oi.price_at_purchase * oi.quantity) AS total_pedido
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            WHERE o.customer_id = %s
            GROUP BY o.id, o.created_at, o.status
            ORDER BY o.created_at DESC;
        """, (user_id,))

        rows = cursor.fetchall()


        orders = {}
        for row in rows:
            order_id, date, status, total = row

            if order_id not in orders:
                orders[order_id] = {
                    'id': order_id,
                    'created_at': date,
                    'status': status,
                    'total': float(total)
                }


        return {
            'statusCode': 200,
            'body': json.dumps(list(orders.values())),
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