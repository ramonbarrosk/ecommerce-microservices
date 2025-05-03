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