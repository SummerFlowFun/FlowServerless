import json
import boto3
from decimal import Decimal
import uuid
import logging
from boto3.dynamodb.conditions import Key, Attr


client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('users')
tableName = 'users'

def lambda_handler(event, context):
    uuid = event['pathParameters']['id']

    # Retrieve user info from DynamoDB
    response = table.get_item(Key={'id': uuid})
    user_info = response.get('Item', {})

    if not user_info:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'User not found'}),
            'headers': {
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Methods': '*',
                'Content-Type': 'application/json'
            }
        }

    return {
        'statusCode': 200,
        'body': json.dumps(user_info),
        'headers': {
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Methods': '*',
            'Content-Type': 'application/json'
        }
    }
