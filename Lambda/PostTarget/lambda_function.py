import json
import boto3
import time
import logging

import urllib3

client = boto3.client('iot-data', region_name='us-east-1')


def lambda_handler(event, context):
    if 'target' not in event:
        logging.error("Validation Failed - no target parameter in message")
        raise Exception("Couldn't post the item to MQTT due to missing target parameter.")
        return {
            'statusCode': 400,
            'body': json.dumps("Couldn't post the item to MQTT due to missing target parameter.")
        }
    else:
        timestamp = time.time()
        try:
            target = int(event['target'])
        except:
            raise Exception("Target parameter is not integer")
            return {
                'statusCode': 400,
                'body': json.dumps("Couldn't post the item to MQTT because target parameter is not integer.")
            }
        message = {
            'timestamp': timestamp,
            'target_moisture': target
        }

        endpoint = "https://a2zp6jocgepsbs-ats.iot.eu-central-1.amazonaws.com:8443"

        https = endpoint + "/topics/" + "actions" + "?qos=1"

        payload = json.dumps(message)

        conn = urllib3.connection_from_url(
            endpoint,
            cert_file='certificate.pem.crt',
            key_file='private.pem.key',
            ca_certs='AmazonRootCA1.pem',
            cert_reqs='REQUIRED')

        response = conn.request(
            'POST',
            https,
            body=payload
        )
        return {
            'statusCode': 200,
            'body': response.data.decode('utf-8')
        }
