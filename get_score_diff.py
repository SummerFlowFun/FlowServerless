import json
import boto3

def calculate_score_diff(userId, foodId, mealDate):
    # Create a Lambda client
    lambda_client = boto3.client('lambda', region_name='ap-northeast-2')

    # Prepare the payload
    payload = {
        "userId": userId,
        "foodId": foodId,
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
    score_diff = response_payload if response_payload else 0  # Default to 0 if not present

    return score_diff

def lambda_handler(event, context):
    # TODO implement
    parameters = event['queryStringParameters']

    return {
        'headers':
            {
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Methods': '*'
            },
        'statusCode': 200,
        'body': json.dumps({'score_diff':calculate_score_diff(parameters['userId'], parameters['foodId'], parameters['mealDate'])})
    }
