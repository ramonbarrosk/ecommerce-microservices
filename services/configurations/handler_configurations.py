import psycopg2
import os
import sys
import json

from http import HTTPStatus

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token

def handler(event, context):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if event.get("httpMethod") != "POST":
            return {
                'statusCode': HTTPStatus.METHOD_NOT_ALLOWED,
                'body': json.dumps({'error': 'Método não permitido'}),
                'headers': {'Content-Type': 'application/json'}
            }

        body = json.loads(event.get("body", "[]"))

        if not isinstance(body, list) or not body:
            return {
                'statusCode': HTTPStatus.BAD_REQUEST,
                'body': json.dumps({'error': 'Esperado um array de configurações'}),
                'headers': {'Content-Type': 'application/json'}
            }

        atualizados = []
        nao_encontrados = []

        for item in body:
            config_id = item.get("id")
            status = item.get("status")

            if config_id is None or status is None:
                continue 

            cursor.execute("""
                UPDATE configurations
                SET status = %s
                WHERE id = %s
            """, (status, config_id))

            if cursor.rowcount == 0:
                nao_encontrados.append(config_id)
            else:
                atualizados.append(config_id)

        conn.commit()

        return {
            'statusCode': HTTPStatus.OK,
            'body': json.dumps({
                'atualizados': atualizados,
                'nao_encontrados': nao_encontrados,
                'mensagem': f'{len(atualizados)} configurações atualizadas com sucesso.'
            }),
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
