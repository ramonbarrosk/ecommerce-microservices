import psycopg2
import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token


def remove_item_from_cart(user_id, product_id, cursor, conn):
    try:
        cursor.execute("""
            SELECT id FROM orders
            WHERE customer_id = %s AND status = 'pending'
            LIMIT 1;
        """, (user_id,))
        result = cursor.fetchone()

        if not result:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No active cart found'}),
                'headers': {'Content-Type': 'application/json'}
            }

        order_id = result[0]

        cursor.execute("""
            DELETE FROM order_items
            WHERE order_id = %s AND product_id = %s;
        """, (order_id, product_id))

        cursor.execute("""
            SELECT COUNT(*) FROM order_items WHERE order_id = %s;
        """, (order_id,))
        item_count = cursor.fetchone()[0]

        if item_count == 0:
            cursor.execute("""
                DELETE FROM orders WHERE id = %s;
            """, (order_id,))

        conn.commit()

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Item removed from cart successfully'}),
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as e:
        conn.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }

def remove_all_items_cart(cursor, conn):
    try:
        cursor.execute("""
            SELECT id FROM orders
            WHERE customer_id = %s AND status = 'pending'
            LIMIT 1;
        """, (user_id,))
        result = cursor.fetchone()

        if not result:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No active cart found'}),
                'headers': {'Content-Type': 'application/json'}
            }

        order_id = result[0]

        cursor.execute("""
            DELETE FROM order_items
            WHERE order_id = %s;
        """, (order_id))

        cursor.execute("""
            SELECT COUNT(*) FROM order_items WHERE order_id = %s;
        """, (order_id,))
        item_count = cursor.fetchone()[0]

        if item_count == 0:
            cursor.execute("""
                DELETE FROM orders WHERE id = %s;
            """, (order_id,))

        conn.commit()

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'All items from cart removed successfully'}),
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

    conn = get_connection()
    cursor = conn.cursor()
    user_id = user_data['sub']

    if not product_id:
        return remove_all_items_cart(cursor, conn)

    response = remove_item_from_cart(user_id, product_id, cursor, conn)

    cursor.close()
    conn.close()

    return response
