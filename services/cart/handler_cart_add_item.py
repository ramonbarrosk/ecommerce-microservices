import psycopg2
import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token


def add_item_to_cart(user_id, product_id, quantity, cursor, conn):
    try:
        cursor.execute("""
            SELECT id FROM orders
            WHERE customer_id = %s AND status = 'pending'
            LIMIT 1;
        """, (user_id,))
        result = cursor.fetchone()

        if result:
            order_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO orders (customer_id, status)
                VALUES (%s, 'pending') RETURNING id;
            """, (user_id,))
            order_id = cursor.fetchone()[0]
            conn.commit()

        cursor.execute("""
            SELECT id FROM order_items
            WHERE order_id = %s AND product_id = %s;
        """, (order_id, product_id))
        item = cursor.fetchone()

        if item:
            cursor.execute("""
                UPDATE order_items
                SET quantity = quantity + %s
                WHERE order_id = %s AND product_id = %s;
            """, (quantity, order_id, product_id))
        else:
            cursor.execute("SELECT price FROM product WHERE id_product = %s;", (product_id,))
            product_price = cursor.fetchone()

            if not product_price:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'Product not found'}),
                    'headers': {'Content-Type': 'application/json'}
                }

            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase)
                VALUES (%s, %s, %s, %s);
            """, (order_id, product_id, quantity, product_price[0]))

        conn.commit()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Item added to cart successfully',
                'cart_item': {
                    'product_id': product_id,
                    'quantity': quantity
                }
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except Exception as e:
        conn.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
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

    body = json.loads(event['body'])
    product_id = body.get('product_id')
    quantity = body.get('quantity')

    if not product_id or not quantity:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'product_id and quantity are required'}),
            'headers': {'Content-Type': 'application/json'}
        }

    conn = get_connection()
    cursor = conn.cursor()
    user_id = user_data['sub']

    response = add_item_to_cart(user_id, product_id, quantity, cursor, conn)

    cursor.close()
    conn.close()

    return response
