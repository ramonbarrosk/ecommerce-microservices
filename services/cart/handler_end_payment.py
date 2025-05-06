import psycopg2
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token

VALID_PAYMENT_METHODS = ['credit_card', 'pix', 'boleto']

def checkout_order(user_id, cart_items, payment_method, cursor, conn):
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

        total = 0
        item_details = []

        for item in cart_items:
            product_id = item['product_id']
            quantity = item['quantity']

            cursor.execute("SELECT price FROM product WHERE id_product = %s", (product_id,))
            product_row = cursor.fetchone()

            if not product_row:
                raise Exception(f"Product with id {product_id} not found")

            price = float(product_row[0])
            total += price * quantity
            item_details.append((product_id, quantity, price))

        cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))

        for product_id, quantity, price in item_details:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, quantity, price))

        cursor.execute("""
            UPDATE orders
            SET status = 'done',
                payment_method = %s
            WHERE id = %s
        """, (payment_method, order_id))

        cursor.execute("""
            INSERT INTO purchase_history (order_id, customer_id, total_amount, payment_method, purchased_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (order_id, user_id, total, payment_method))

        conn.commit()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Order placed successfully',
                'order': {
                    'order_id': order_id,
                    'status': 'confirmed',
                    'payment_method': payment_method,
                    'total': round(total, 2)
                }
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
        cart_items = body.get('cart_items', [])
        payment_method = body.get('payment_method')

        if not cart_items or not payment_method:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing cart_items or payment_method'}),
                'headers': {'Content-Type': 'application/json'}
            }

        conn = get_connection()
        cursor = conn.cursor()
        user_id = user_data['sub']

        response = checkout_order(user_id, cart_items, payment_method, cursor, conn)

        cursor.close()
        conn.close()
        return response

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }
