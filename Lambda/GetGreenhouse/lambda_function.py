import json
import time
from datetime import datetime, timedelta
import boto3
from boto3.dynamodb.conditions import Key, Attr
import logging
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('status')

def handle_decimal_type(obj):
  if isinstance(obj, Decimal):
      if float(obj).is_integer():
         return int(obj)
      else:
         return float(obj)
  raise TypeError

def lambda_handler(event, context):
    now = int(datetime.timestamp(datetime.now()))
    if "days_ago" not in json.dumps(event):
        #No parameter
        time_ago =  int(datetime.timestamp(datetime.now() - timedelta(days=365)))
        filter = Key('timestamp').between(time_ago,now)
        response = table.scan(
                        FilterExpression=filter
        )
        max = 0
        max_record = {}
        response = json.dumps(response["Items"], default=handle_decimal_type)
        response = json.loads(response)
        for record in response:
            if int(record['timestamp']) > max:
                max = int(record['timestamp'])
                max_record = record
        response = max_record
        #response = json.dumps(response, default=handle_decimal_type)
        return {
            'statusCode': 200,
            'body': json.dumps(response, default=handle_decimal_type)
        }
    else:
        #Has parameter
        time_ago = int(datetime.timestamp(datetime.now() - timedelta(int(event["queryStringParameters"]["days_ago"]))))
        filter = Key('timestamp').between(time_ago,now)
        response = table.scan(
                        FilterExpression=filter
        )
    return {
        'statusCode': 200,
        'body': json.dumps(response["Items"], default=handle_decimal_type)
    }
