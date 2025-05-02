import psycopg2
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
import bcrypt
import jwt
from datetime import datetime, timedelta
SECRET_KEY = os.getenv('JWT_SECRET_KEY')

def handler(event, context):
    body = event.get('body')
    if not body:
        return {
            'statusCode': 400,
            'body': 'Bad Request: Missing body'
        }
    
    try:
        data = json.loads(body)
        email = data['email']
        password = data['password']
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': f'Missing field: {str(e)}'
        }

    if not email or not password:
        return {
            'statusCode': 400,
            'body': 'Both email and password are required'
        }

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, name, password FROM customers WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return {
                'statusCode': 401,
                'body': 'Invalid credentials'
            }

        user_id, name, hashed_password = user

        if isinstance(hashed_password, memoryview):
            hashed_password = bytes(hashed_password)

        if hashed_password is None:
            return {
                'statusCode': 401,
                'body': 'Invalid credentials'
            }

        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return {
                'statusCode': 401,
                'body': 'Invalid credentials'
            }

        expiration = datetime.utcnow() + timedelta(hours=1)
        payload = {
            'sub': str(user_id),
            'name': name,
            'exp': expiration
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return {
            'statusCode': 200,
            'body': json.dumps({'token': token})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }

    finally:
        cursor.close()
        conn.close()