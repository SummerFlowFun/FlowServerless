import json
import boto3
from decimal import Decimal
import uuid
import logging
from boto3.dynamodb.conditions import Key, Attr


client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('foods_origin_table')
tableName = 'foods_origin_table'

# Custom JSON Encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    query = event['queryStringParameters']['query']
    last_evaluated_key = event['queryStringParameters'].get('lastEvaluatedKey',None)
    # Retrieve user info from DynamoDB
    scan_kwargs = {
        'FilterExpression': Attr('식품명').contains(query)
    }
    if last_evaluated_key:
        scan_kwargs['ExclusiveStartKey'] = { "id": last_evaluated_key}

    # Perform the scan operation
    response = table.scan(**scan_kwargs)

    # Append the items to the results list

    # Check if there's more data to retrieve
    last_evaluated_key = response.get('LastEvaluatedKey')
    food_infos = response.get('Items', [])
    print(food_infos)
    if not food_infos or len(food_infos) == 0:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Foods not found'}),
            'headers': {
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Methods': '*',
                'Content-Type': 'application/json'
            }
        }

    return {
        'statusCode': 200,
        'body': json.dumps( {"foodInfos":food_infos, "lastEvaluatedKey": last_evaluated_key}, cls=DecimalEncoder, ensure_ascii=False),
        'headers': {
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Methods': '*',
            'Content-Type': 'application/json'
        }
    }
