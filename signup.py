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

class DuplicateError(Exception):
    pass

def response_handler(statusCode, body):
    json.dumps(body)
    return {
        "statusCode": statusCode,
        "headers": {
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Methods': '*',
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    logging.info(f"Received event: {json.dumps(event)}")
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
        body = {'message' : 'Parameter Key Error : '+str(e)}
        return response_handler(statusCode, body)
    try:

        check = table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email))
        if check and check['Count'] > 0:
            print(check)
            raise DuplicateError
        response = table.put_item(
            Item={
                'id': str(uuid.uuid4()),
                'email': email,
                'password': password
            })
        body = {
            'id': str(uuid.uuid4()),
            'email': email,
            'password': password
        }
    except DuplicateError:
        statusCode = 409
        body = {'message':'The email already exists'}
        return response_handler(statusCode, body)
    return response_handler(statusCode, body)