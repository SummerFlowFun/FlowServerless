import json
import boto3
from decimal import Decimal
import uuid
import logging
import time
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
foodTable = dynamodb.Table('foods_origin_table')
userTable = dynamodb.Table('users')
userDailyInfoTable = dynamodb.Table('user_daily_info')
nutritionTable = dynamodb.Table('NutritionData')
import math

def logistic_score(contribution):
    # Scale the logistic function so that it asymptotically approaches 40 for large positive contributions
    # and 14 for large negative contributions.
    L = 40  # Upper asymptote
    k = 0.5  # Slope of the curve
    x0 = 27  # Midpoint of the curve (center of the transition between 14 and 40)

    score = 14 + (L - 14) / (1 + math.exp(-k * (contribution - x0)))

    return score

def calculate_nutrient_score(food_value, recommended_value):
    if recommended_value is None or recommended_value == 0:
        return 0
    contribution = (food_value / recommended_value) * 100

    return logistic_score(float(contribution))
    # if 80 <= contribution <= 120:
    #     return 30  # ideal range
    # elif 60 <= contribution < 80 or 120 < contribution <= 140:
    #     return 20  # acceptable range
    # elif 40 <= contribution < 60 or 140 < contribution <= 160:
    #     return 10  # suboptimal range
    # else:
    #     return 0  # poor range


def calculate_total_score(food_info, nutrition_info):
    total_score = 0
    count = 0
    for nutrient, recommended_value in nutrition_info.items():
        if nutrient in food_info and food_info[nutrient] is not None:
            food_value = food_info[nutrient]
            score = calculate_nutrient_score(Decimal(food_value), Decimal(recommended_value))
            total_score += score
            count += 1

    if count == 0:
        return 0  # No nutrients to compare
    return total_score / count  # Average score

def lambda_handler(event, context):
    userId = event['userId']
    foodId = event['foodId']
    mealDate = event['mealDate']

    userInfo = userTable.get_item(Key={'id':userId}).get('Item',{})

    userDailyInfo = userDailyInfoTable.query(IndexName="userId-mealDate-index", KeyConditionExpression=Key('userId').eq(userId) & Key('mealDate').eq(mealDate), Limit=1)
    userDailyInfo = userDailyInfo.get('Item',{})

    foodInfo = foodTable.get_item(Key={'id':foodId}).get('Item',{})

    start = datetime.strptime(userInfo.get('pregnantDate','2024-08-11'), "%Y-%m-%d")
    now = datetime.now()
    diff_time = abs((now - start).total_seconds())
    diff_weeks = int(diff_time // (7 * 24 * 60 * 60))+1

    queryKeyword = str(diff_weeks)+'주차'
    nutritionInfo = nutritionTable.query(KeyConditionExpression=Key('임신 주수').eq(queryKeyword)).get('Items')[0]
    score = calculate_total_score(foodInfo, nutritionInfo)
    print("FoodInfo", foodInfo)
    print("nutritionInfo", nutritionInfo)

    return int(score)
