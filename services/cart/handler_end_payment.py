import psycopg2
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token

VALID_PAYMENT_METHODS = ['credit_card', 'pix', 'boleto']

def checkout_order(user_id, payment_method, cursor, conn):
    if payment_method not in VALID_PAYMENT_METHODS:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid payment method'}),
            'headers': {'Content-Type': 'application/json'}
        }

    try:
        cursor.execute("""
            SELECT id FROM orders
            WHERE customer_id = %s AND status = 'pending'
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        order_row = cursor.fetchone()

        if not order_row:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No pending order found'}),
                'headers': {'Content-Type': 'application/json'}
            }

        order_id = order_row[0]

        # Atualiza status e método de pagamento
        cursor.execute("""
            UPDATE orders
            SET status = 'done',
                payment_method = %s
            WHERE id = %s
        """, (payment_method, order_id))

        conn.commit()

        # Busca os detalhes do pedido finalizado
        cursor.execute("""
            SELECT 
                o.id AS id,
                p.name AS product_name,
                p.description AS product_description,
                oi.quantity,
                oi.price_at_purchase,
                oi.id AS item_id,
                p.picture_url
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            JOIN product p ON p.id_product = oi.product_id
            WHERE o.id = %s
        """, (order_id,))

        rows = cursor.fetchall()

        order_details = {
            'order_id': order_id,
            'status': 'confirmed',
            'payment_method': payment_method,
            'items': []
        }

        for row in rows:
            order_details['items'].append({
                'product_name': row[1],
                'product_description': row[2],
                'quantity': row[3],
                'price_at_purchase': float(row[4]),
                'item_id': row[5],
                'picture_url': row[6]
            })

        total = sum(item['quantity'] * item['price_at_purchase'] for item in order_details['items'])
        order_details['total'] = round(total, 2)
        order_details['total_count'] = len(order_details['items'])

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Order placed successfully',
                'order': order_details
            }),
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as e:
        conn.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }

def handler(event, context):
    token = event['headers'].get('Authorization', '').replace('Bearer ', '')
    user_data = validate_token(token)

    if not user_data:
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Unauthorized'}),
            'headers': {'Content-Type': 'application/json'}
        }

    try:
        body = json.loads(event['body'])
        payment_method = body.get('payment_method')

        if not payment_method:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing payment_method'}),
                'headers': {'Content-Type': 'application/json'}
            }

        conn = get_connection()
        cursor = conn.cursor()
        user_id = user_data['sub']

        response = checkout_order(user_id, payment_method, cursor, conn)

        cursor.close()
        conn.close()
        return response

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }
