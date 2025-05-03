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

def get_coordinates(name):
    json_path = Path('MunicipiosBrasil.json')
    with open(json_path, 'r', encoding='utf-8') as f:
      municipalities = json.load(f)

    for m in municipalities:
        if m[4] == name:
            lat = float(m[1].replace(',', '.'))
            long = float(m[2].replace(',', '.'))
            return lat, long
    
    return False

def calculate_distance(cep):
    city = ''

    if len(cep) == 8:
        link = f'https://viacep.com.br/ws/{cep}/json/'

        request = requests.get(link)

        dic_request = request.json()

        city = dic_request['localidade']
    else:
        return False

    name = unidecode(city).upper()

    lat, long = get_coordinates(name)

    if lat == False: return False
    if long == False: return False

    destination = [lat, long]

    origin = ['-9.645', '-35.733']
    distance = geodesic(origin, destination).kilometers

    return round(distance, 2) 

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
    
    distance = calculate_distance(cep)
    base_price = 10.00
    price_per_km = 0.10
    shipping_price = base_price + (shipping * price_per_km)

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
            'body': json.dumps({'frete': shipping_price}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }