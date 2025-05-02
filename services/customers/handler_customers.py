import psycopg2
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
import bcrypt

def handler(event, context):
    body = event.get('body')
    if not body:
        return {
            'statusCode': 400,
            'body': 'Bad Request: Missing body'
        }
    
    try:
        data = json.loads(body)
        name = data['name']
        email = data['email']
        password = data['password']
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': f'Missing field: {str(e)}'
        }

    if not name or not email or not password:
        return {
            'statusCode': 400,
            'body': 'All fields are required (name, email, password)'
        }

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO customers (name, email, password)
            VALUES (%s, %s, %s)
        """, (name, email, hashed_password))

        conn.commit()

        return {
            'statusCode': 201,
            'body': f'Customer {name} created successfully!'
        }

    except psycopg2.Error as e:
        conn.rollback()
        return {
            'statusCode': 500,
            'body': f'Database error: {str(e)}'
        }

    finally:
        cursor.close()
        conn.close()