from awscrt import mqtt

def publish(mqtt_connection, topic, message):
	print("Publishing message to topic '{}': {}".format(topic, message))
	mqtt_connection.publish(
	    topic=topic,
	    payload=message,
	    qos=mqtt.QoS.AT_LEAST_ONCE)