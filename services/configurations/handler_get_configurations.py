import psycopg2
import os
import sys
import json
from http import HTTPStatus
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection

def handler(event, context):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if event.get("httpMethod") != "GET":
            return {
                'statusCode': HTTPStatus.METHOD_NOT_ALLOWED,
                'body': json.dumps({'error': 'Método não permitido'}),
                'headers': {'Content-Type': 'application/json'}
            }

        cursor.execute("SELECT id, status FROM configurations")  # ajuste os campos conforme necessário
        rows = cursor.fetchall()

        configs = [
            {'id': row[0], 'status': row[1]}
            for row in rows
        ]

        return {
            'statusCode': HTTPStatus.OK,
            'body': json.dumps(configs),
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as e:
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }

    finally:
        cursor.close()
        conn.close()
