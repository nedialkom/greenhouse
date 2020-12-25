import connection
import grovepi
import json
import time
from awscrt import mqtt

# environment variables
endpoint = 'a2zp6jocgepsbs-ats.iot.eu-central-1.amazonaws.com'
cert = 'certificate.pem.crt'
pri_key = 'private.pem.key'
root_ca = 'AmazonRootCA1.pem'
client_id = 'nedialko'

# NOTE:
# The wiki:                Observer:
# 		    Min  Typ  Max  value    Condition
# 		    0    0    0    0        sensor in open air
# 		    0    20   300  18       sensor in dry soil
# 		    300  580  700  425      sensor in humid soil
# 		    700  940  950  690      sensor in water

target_moisture = 400
relay_target_state = 'off'  # 'on' or 'off'
relay_current_state = 'off'  # 'on' or 'off'
mode = 'auto'  # 'auto' or 'manual'

refresh_frequency = 5  # in seconds; how often moisture sensor will update data and send to DB


def get_moisture():
    # Connect the Grove Moisture Sensor to analog port A0
    # SIG,NC,VCC,GND
    sensor = 0
    try:
        return grovepi.analogRead(sensor)
    except IOError:
        return None


def relay(state):
    relay_port = 4
    grovepi.pinMode(relay_port, "OUTPUT")
    try:
        if state == 'on':
            grovepi.digitalWrite(relay_port, 1)
            print("relay is now on")
            return True
        elif state == 'off':
            grovepi.digitalWrite(relay_port, 0)
            print("relay is now off")
            return True
        else:
            return False
    except IOError:
        return False


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, **kwargs):
    # to define actions when certain message is received
    payload = json.loads(payload)
    print(payload)
    global relay_current_state
    global target_moisture
    global mode
    if 'relay' in payload and topic == 'actions':
        if payload['relay'] == 'on':
            if relay_current_state == 'off':
                print('Turning relay on')
                if relay('on'):
                    print('Action completed')
                    relay_current_state = 'on'
                else:
                    print('Action was not successfully executed')
            elif relay_current_state == 'on':
                print('Relay is already on')
        elif payload['relay'] == 'off':
            if relay_current_state == 'on':
                print('Turning relay off')
                if relay('off'):
                    print('Action completed')
                    relay_current_state = 'off'
                else:
                    print('Action was not successfully executed')
        else:
            print('Unknown command for relay')
    elif 'mode' in payload:
        if payload['mode'] == 'auto':
            if mode == 'manual':
                mode = 'auto'
                print('Mode changed to auto!')
            else:
                print('Mode is already auto!')
        elif payload['mode'] == 'manual':
            if mode == 'auto':
                mode = 'manual'
                print('Mode changed to manual!')
            else:
                print('Mode is already manual!')
        else:
            print('Unknown mode')
    elif 'target_moisture' in payload:
        target_moisture = int(payload['target_moisture'])
    else:
        print('Unknown object - only relay, mode and target_moisture are accepted')

    # publish with updated status
    moisture = get_moisture()
    if moisture < target_moisture:
        relay_target_state = 'on'
    else:
        relay_target_state = 'off'

    topic_status = 'status'
    timestamp = int(time.time())
    message = json.dumps({'current moisture': moisture,
                          'target moisture': target_moisture,
                          'mode': mode,
                          'relay target status': relay_target_state,
                          'relay_current_state': relay_current_state,
                          'timestamp': timestamp
                          })
    global mqtt_connection
    publish(mqtt_connection, topic_status, message)
    print('Published updated status')


def subscribe(topic, subscribe_connection):
    print("Subscribing to topic '{}'...".format(topic))
    subscribe_future, packet_id = subscribe_connection.subscribe(
        topic=topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))


def publish(publish_connection, topic, publish_message):
    print("{}: {}".format(topic, message))
    publish_connection.publish(
        topic=topic,
        payload=publish_message,
        qos=mqtt.QoS.AT_LEAST_ONCE)


# connect
mqtt_connection = connection.connect(endpoint, cert, pri_key, root_ca, client_id)

# subscribe to Relay channel
topic_actions = "actions"
subscribe(topic_actions, mqtt_connection)

# Loop for sensor reading
while True:
    try:
        moisture = get_moisture()
        if moisture < target_moisture:
            relay_target_state = 'on'
        else:
            relay_target_state = 'off'
        topic_status = 'status'
        timestamp = int(time.time())
        message = json.dumps({'current moisture': moisture,
                              'target moisture': target_moisture,
                              'mode': mode,
                              'relay target status': relay_target_state,
                              'relay_current_state': relay_current_state,
                              'timestamp': timestamp
                              })
        # Publish message to Humidity channel
        publish(mqtt_connection, topic_status, message)
        if mode == 'auto' and relay_target_state != relay_current_state:
            if relay_target_state == 'on':
                if relay('on'):
                    print('Relay automatically on')
                    relay_current_state = 'on'
                else:
                    print('Error turning on relay')
            elif relay_target_state == 'off':
                if relay('off'):
                    print('Relay automatically off')
                    relay_current_state = 'off'
                else:
                    print('Error turning off relay')
        time.sleep(refresh_frequency)
    except KeyboardInterrupt:
        break


# Disconnect
print("Disconnecting...")
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
print("Disconnected!")
