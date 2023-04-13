import os
import boto3
import urllib.request
import json

dynamodb = boto3.resource('dynamodb')
table_criptos = os.environ['TABLE_CRIPTOS']
table = dynamodb.Table(table_criptos)

def save_criptos(event, context):
    def getCriptos():
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?slug=bitcoin,ethereum'
        headers = {'X-CMC_PRO_API_KEY': '3298642378'}
        try:
            #! Hacemos la petición a la API para traernos los valores del Bitcoin y Ethereum
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req)
            data = json.loads(response.read().decode())
            #? Creamos un diccionario para almacenar la hora de la consulta y los valores en dólares del bitcoin y el ethereum
            datos_table = {}
            datos_table['time'] = data['status']['timestamp']
            #! Extraemos los datos de las criptomonedas y las almacenamos en la variable criptos
            criptos = data['data']
            for item in criptos:
                datos_table[criptos[item]['name']] = criptos[item]['quote']['USD']['price']

            #? Retornamos el diccionario con los datos para que se puedan almacenar en la base de datos
            return datos_table
        except:
            print('error')

    resultado = getCriptos()
    
    try:
        item = {
            'time': resultado['time'],
            'Bitcoin': str(resultado['Bitcoin']),
            'Ethereum': str(resultado['Ethereum'])
        }
        response = table.put_item(Item=item)
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }

    except:
        return {
            'statusCode': 400,
            'body': json.dumps('Error!')
        }


def get_criptos(event, context):
    
    response = table.scan()
    items = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': True
    }

    sorted_items = sorted(items, key=lambda x: x['time'])
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(sorted_items)
    }
    