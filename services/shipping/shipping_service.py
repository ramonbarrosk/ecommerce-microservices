import psycopg2
import os
import sys
import json
import requests
from unidecode import unidecode
from geopy.distance import geodesic
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from db import get_connection
from auth import validate_token

json_path = 'services/shipping/MunicipiosBrasil.json'

def get_coordenadas(name):
    municipalities = json.load(json_path)

    for m in municipalities:
        if m[4] == name:
            return m[1], m[2]
    
    return False

def calculate_shipping(cep):

    cidade = ''

    if len(cep) == 8:
        link = f'https://viacep.com.br/ws/{cep}/json/'

        requisicao = requests.get(link)

        print(requisicao)

        dic_requisicao = requisicao.json()

        cidade = dic_requisicao['localidade']
    else:
        return False

    nome = unidecode(cidade).upper()

    latitude, longitude = get_coordenadas(nome)

    if latitude == False: return False
    if longitude == False: return False

    origem = [-9.645, -35.733]
    distancia = geodesic(origem, destino).kilometers

    return round(distancia, 2)    

def handler(event, context):
    #token = event['headers'].get('Authorization', '').replace('Bearer ', '')

    user_data = validate_token(token)
    # if not user_data:
    #     return {
    #         'statusCode': 401,
    #         'body': json.dumps({'message': 'Unauthorized'})
    #     }
    
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

    if shipping == False:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'CEP INVALIDO'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    return {
            'statusCode': 200,
            'body': json.dumps({'frete': shipping}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }