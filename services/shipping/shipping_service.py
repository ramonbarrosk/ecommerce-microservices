import psycopg2
import os
import sys
import json
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token

def calculate_shipping(cep):
    shipping = 10 + random.uniform(10, 20)
    return round(shipping, 2)    

def handler(event, context):
    token = event['headers'].get('Authorization', '').replace('Bearer ', '')

    user_data = validate_token(token)
    if not user_data:
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Unauthorized'})
        }
    
    body = json.loads(event.get('body', {}))
    cep = body.get('cep')

    if not cep:
        return {
              'statusCode': 400,
              'body': json.dumps({'message':'Dados Incompletos'}),
              'headers': {
                  'Content-Type': 'application/json'
              }
        }
    
    shipping = calculate_shipping(cep) 

    return {
            'statusCode': 200,
            'body': json.dumps({'frete': shipping}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }