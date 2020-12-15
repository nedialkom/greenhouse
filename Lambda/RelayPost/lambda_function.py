import json
import boto3
import time
import logging

import urllib3

client = boto3.client('iot-data', region_name='us-east-1')


def lambda_handler(event, context):
    print(event)
    if 'relay' not in event:
        logging.error("Validation Failed - no relay parameter in message")
        raise Exception("Couldn't post the item to MQTT due to missing relay parameter.")
        return {
            'statusCode': 400,
            'body': json.dumps("Couldn't post the item to MQTT due to missing relay parameter.")
        }
    else:
        timestamp = time.time()
        if event['relay'] == 'on' or event['relay'] == 'off':
            message = {
                'timestamp': timestamp,
                'relay': event['relay']
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
                'body': response.data
            }
        else:
            logging.error("Invalid 'relay' parameter. Only 'on' or 'off' are accepted.")
            raise Exception(
                "Couldn't post the item to MQTT due to invalid relay parameter - only 'on' or 'off' are accepted.")
            return {
                'statusCode': 400,
                'body': json.dumps(
                    "Couldn't post the item to MQTT due to invalid relay parameter - only 'on' or 'off' are accepted.")
            }

