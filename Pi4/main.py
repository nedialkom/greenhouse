import connection
import subscription
import publication
import grovepi
import json
import time

def get_moisture():
    # Connect the Grove Moisture Sensor to analog port A0
    # SIG,NC,VCC,GND
    sensor = 0
    try:
        return grovepi.analogRead(sensor)
    except IOError:
        return None

# environment variables
endpoint = 'a2zp6jocgepsbs-ats.iot.eu-central-1.amazonaws.com'
cert = 'certificate.pem.crt'
pri_key = 'private.pem.key'
root_ca = 'AmazonRootCA1.pem'
client_id = 'nedialko'

# connect
mqtt_connection = connection.connect(endpoint, cert, pri_key, root_ca, client_id)

# subscribe to Relay channel
topic = r"pi4 \relay\details"
subscription1 = subscription.subscribe(topic, mqtt_connection)

# Loop for sensor reading
while True:
    try:
        message = json.dumps({'moisture': get_moisture()})
        # Publish message to Humidity channel
        topic = r'pi4\humidity\details'
        publication.publish(mqtt_connection, topic, message)
        time.sleep(1)
    except KeyboardInterrupt:
        break


# Disconnect
print("Disconnecting...")
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
print("Disconnected!")