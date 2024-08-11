import json
import boto3
from decimal import Decimal
import uuid
import logging
from boto3.dynamodb.conditions import Key, Attr


client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
userMealsTable = dynamodb.Table('user_meals')
userTable = dynamodb.Table('users')
foodTable = dynamodb.Table('foods_origin_table')
userDailyInfoTable = dynamodb.Table('user_daily_info')

# Custom JSON Encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def calculate_score_diff(user_daily_info, food, mealDate):
    # Create a Lambda client
    lambda_client = boto3.client('lambda', region_name='ap-northeast-2')

    # Prepare the payload
    payload = {
        "userId": user_daily_info['userId'],
        "foodId": food['id'],
        "mealDate": mealDate
    }

    # Invoke the Lambda function
    response = lambda_client.invoke(
        FunctionName='arn:aws:lambda:ap-northeast-2:107378961181:function:CalculateScoreDiff',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    # Read the response
    response_payload = json.loads(response['Payload'].read())

    # Extract the score difference from the response
    score_diff = response_payload if response_payload else 0

    return score_diff

def lambda_handler(event, context):
    body = json.loads(event['body'])
    # Retrieve user info from DynamoDB
    try:
        user_id = body['userId']
        food_id = body['foodId']
        meal_type = body['mealType']
        meal_date = body['mealDate']
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Key error'+ str(e)}),
            'headers': {
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Methods': '*',
                'Content-Type': 'application/json'
            }
        }

    user = userTable.get_item(Key={'id':user_id})
    user = user.get('Item', {})
    if not user:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Users not found'}),
            'headers': {
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Methods': '*',
                'Content-Type': 'application/json'
            }
        }

    food = foodTable.get_item(Key={'id':food_id})
    food = food.get('Item', {})
    if not food:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Food not found'}),
            'headers': {
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Methods': '*',
                'Content-Type': 'application/json'
            }
        }

    user_daily_info = userDailyInfoTable.query(IndexName="userId-mealDate-index", KeyConditionExpression=Key('userId').eq(user_id) & Key('mealDate').eq(meal_date), Limit=1)
    user_daily_info = user_daily_info.get('Item',{})
    user_daily_info[meal_type] = user_daily_info.get(meal_type, [])
    user_daily_info[meal_type].append(food_id)

    origin_score = user_daily_info.get('score',0)
    user_daily_info['userId'] = user_id
    user_daily_info['mealDate'] = meal_date

    diff_score = calculate_score_diff(user_daily_info, food, meal_date)
    user_daily_info['score'] = origin_score + diff_score
    user_daily_info['id'] = str(uuid.uuid4())
    userDailyInfoTable.put_item(Item=user_daily_info)

    return {
        'statusCode': 200,
        'body': json.dumps(user_daily_info, cls=DecimalEncoder, ensure_ascii=False),
        'headers': {
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Methods': '*',
            'Content-Type': 'application/json'
        }
    }
