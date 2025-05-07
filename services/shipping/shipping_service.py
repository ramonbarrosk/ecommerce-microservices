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

municipalities_path = 'services/shipping/MunicipiosBrasil.json'

def get_coordinates(name):
    json_path = Path(municipalities_path)
    with open(json_path, 'r', encoding='utf-8') as f:
      municipalities = json.load(f)

    for m in municipalities:
        if m[4] == name:
            lat = float(m[1].replace(',', '.'))
            long = float(m[2].replace(',', '.'))
            return lat, long
    
    return False, False

def calculate_distance(cep):
    city = ''

    if len(cep) != 8:
        return False

    try:
        link = f'https://viacep.com.br/ws/{cep}/json/'
        response = requests.get(link, timeout=5)

        response.raise_for_status()
        data = response.json()

        if 'erro' in data:
            return False 

        complete_json = data
        city = data.get('localidade')
        if not city:
            return False

        name = unidecode(city).upper()

        lat, long = get_coordinates(name)
        if lat is False or long is False:
            return False

        destination = [lat, long]
        origin = [-9.645, -35.733]
        distance = geodesic(origin, destination).kilometers

        return [round(distance, 2), complete_json]

    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Erro ao calcular distância: {e}")
        return False

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
    
    result = calculate_distance(cep)
    if not result:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'CEP INVALIDO OU INEXISTENTE'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    distance, result_json = result

    base_price = 10.00
    price_per_km = 0.10
    shipping_price = base_price + (distance * price_per_km)
    result_json['frete'] = shipping_price

    return {
            'statusCode': 200,
            'body': json.dumps(result_json),
            'headers': {
                'Content-Type': 'application/json'
            }
        }