from awscrt import mqtt

# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, **kwargs):
    # to define actions when certain message is recieved
    topic_parsed = False
    if "/" in topic:
        parsed_topic = topic.split("/")
        if len(parsed_topic) == 3:
            # this topic has the correct format
            if (parsed_topic[0] == 'pi') and (parsed_topic[2] == 'details'):
                # this is a topic we care about, so check the 2nd element
                if (parsed_topic[1] == 'humidity'):
                    print("Received humidity request: {}".format(payload))
                    topic_parsed = True
                if (parsed_topic[1] == 'relay'):
                    print("Received relay status: {}".format(payload))
                    topic_parsed = True
    if not topic_parsed:
        print("Unrecognized message topic.")
    print("Received message from topic '{}': {}".format(topic, payload))


def subscribe(topic, mqtt_connection):
    print("Subscribing to topic '{}'...".format(topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))