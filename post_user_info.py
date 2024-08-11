import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

def lambda_handler(event, context):
    # Extract user info from the request body
    uuid = event['pathParameters']['id']
    body = json.loads(event['body'])
    isPregnant = body.get('isPregnant', False)
    pregnantDate = body.get('pregnantDate')
    illness = body.get('illness', [])

    # Fetch existing user info if available
    response = table.get_item(Key={'id': uuid})
    user_info = response.get('Item', {})

    # Update the user info
    if not user_info:
        # If user info does not exist, create it
        user_info = {
            'id': uuid,
            'isPregnant': isPregnant,
            'pregnant': pregnantDate,
            'illness': illness
        }
    else:
        # Update existing user info
        user_info['isPregnant'] = isPregnant
        if pregnantDate:
            user_info['pregnantDate'] = pregnantDate
        if illness:
            user_info['illness'] = illness

    # Put the updated user info back into the table
    table.put_item(Item=user_info)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'User info updated successfully',
            'userInfo': user_info
        }),
        'headers': {
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Methods': '*',
            'Content-Type': 'application/json'
        }
    }