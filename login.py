import json
import boto3
from decimal import Decimal

from boto3.dynamodb.conditions import Key

client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('users')
tableName = 'users'


class NotUserError(Exception):
    pass

def response_handler(statusCode, body):
    res = {
        "statusCode": statusCode,
        "headers": {
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Methods': '*',
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }
    return res

def lambda_handler(event, context):
    body = {}
    statusCode = 200
    headers = {
        "Content-Type": "application/json"
    }
    payload = json.loads(event['body'])
    try:
        email = payload['email']
        password = payload['password']
    except Exception as e:
        statusCode = 400
        body = {'message': 'Parameter KeyError: '+ str(e)}
        return response_handler(statusCode, body)
    try:
        response = table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email))
        if response['Count'] <= 0 or response['Items'][0]['password'] != password:
            raise NotUserError
        if not table:
            raise NotUserError
        body = response['Items'][0]
    except NotUserError:
        statusCode = 403
        body = {'message': 'Not authorized'}
        return response_handler(statusCode, body)

    return response_handler(statusCode, body)