'''
**********************************************************************
* Filename    : pizerodht11.py
* Description : Demonstration of DHT11 humiture & temperature model with Azure IoT Hub
* Author      : Spence Kile
* E-mail      : spence.kile@acuitybrands.com
**********************************************************************
'''

import RPi.GPIO as GPIO
import time
import json
import sys

import iothub_client

from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult

from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

from iothub_client_args import get_iothub_opt, OptionError

# HTTP options

# Because it can poll "after 9 seconds" polls will happen effectively

# at ~10 seconds.

# Note that for scalabilty, the default value of minimumPollingTime

# is 25 minutes. For more information, see:

# https://azure.microsoft.com/documentation/articles/iot-hub-devguide/#messaging

TIMEOUT = 241000

MINIMUM_POLLING_TIME = 9



# messageTimeout - the maximum time in milliseconds until a message times out.

# The timeout period starts at IoTHubClient.send_event_async.

# By default, messages do not expire.

MESSAGE_TIMEOUT = 10000

RECEIVE_CONTEXT = 0
RECEIVED_COUNT = 0
TWIN_CONTEXT = 0
SEND_REPORTED_STATE_CONTEXT = 0
METHOD_CONTEXT = 0

DHTPIN = 17

GPIO.setmode(GPIO.BCM)

MAX_UNCHANGE_COUNT = 11

STATE_INIT_PULL_DOWN = 1
STATE_INIT_PULL_UP = 2
STATE_DATA_FIRST_PULL_DOWN = 3
STATE_DATA_PULL_UP = 4
STATE_DATA_PULL_DOWN = 5

# chose HTTP, AMQP or MQTT as transport protocol

PROTOCOL = IoTHubTransportProvider.MQTT

# String containing Hostname, Device Id & Device Key in the format:

# "HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>"

CONNECTION_STRING = "[Device Connection String]"

MSG_TXT = "{\"deviceId\": \"pizerow\",\"temperatureC\": \"%s\",\"humidity\": \"%s\"}"

def read_dht11_dat():
	GPIO.setup(DHTPIN, GPIO.OUT)
	GPIO.output(DHTPIN, GPIO.HIGH)
	time.sleep(0.05)
	GPIO.output(DHTPIN, GPIO.LOW)
	time.sleep(0.02)
	GPIO.setup(DHTPIN, GPIO.IN, GPIO.PUD_UP)

	unchanged_count = 0
	last = -1
	data = []
	while True:
		current = GPIO.input(DHTPIN)
		data.append(current)
		if last != current:
			unchanged_count = 0
			last = current
		else:
			unchanged_count += 1
			if unchanged_count > MAX_UNCHANGE_COUNT:
				break

	state = STATE_INIT_PULL_DOWN

	lengths = []
	current_length = 0

	for current in data:
		current_length += 1

		if state == STATE_INIT_PULL_DOWN:
			if current == GPIO.LOW:
				state = STATE_INIT_PULL_UP
			else:
				continue
		if state == STATE_INIT_PULL_UP:
			if current == GPIO.HIGH:
				state = STATE_DATA_FIRST_PULL_DOWN
			else:
				continue
		if state == STATE_DATA_FIRST_PULL_DOWN:
			if current == GPIO.LOW:
				state = STATE_DATA_PULL_UP
			else:
				continue
		if state == STATE_DATA_PULL_UP:
			if current == GPIO.HIGH:
				current_length = 0
				state = STATE_DATA_PULL_DOWN
			else:
				continue
		if state == STATE_DATA_PULL_DOWN:
			if current == GPIO.LOW:
				lengths.append(current_length)
				state = STATE_DATA_PULL_UP
			else:
				continue
	if len(lengths) != 40:
		#print "Data not good, skip"
		return False

	shortest_pull_up = min(lengths)
	longest_pull_up = max(lengths)
	halfway = (longest_pull_up + shortest_pull_up) / 2
	bits = []
	the_bytes = []
	byte = 0

	for length in lengths:
		bit = 0
		if length > halfway:
			bit = 1
		bits.append(bit)
	#print "bits: %s, length: %d" % (bits, len(bits))
	for i in range(0, len(bits)):
		byte = byte << 1
		if (bits[i]):
			byte = byte | 1
		else:
			byte = byte | 0
		if ((i + 1) % 8 == 0):
			the_bytes.append(byte)
			byte = 0
	#print the_bytes
	checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
	if the_bytes[4] != checksum:
		#print "Data not good, skip"
		return False

	return the_bytes[0], the_bytes[2]

def set_certificates(client):
    from iothub_client_cert import CERTIFICATES
    try:
        client.set_option("TrustedCerts", CERTIFICATES)
        print ( "set_option TrustedCerts successful" )
    except IoTHubClientError as iothub_client_error:
        print ( "set_option TrustedCerts failed (%s)" % iothub_client_error )

def receive_message_callback(message, counter):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "Received Message [%d]:" % counter )
    print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    counter += 1
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
    return IoTHubMessageDispositionResult.ACCEPTED


def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    print ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
    #map_properties = message.properties()
    #print ( "    message_id: %s" % message.message_id )
    #print ( "    correlation_id: %s" % message.correlation_id )
    #key_value_pair = map_properties.get_internals()
    #print ( "    Properties: %s" % key_value_pair )
    #SEND_CALLBACKS += 1
    #print ( "    Total calls confirmed: %d" % SEND_CALLBACKS )


def device_twin_callback(update_state, payload, user_context):
    global TWIN_CALLBACKS
    print ( "\nTwin callback called with:\nupdateStatus = %s\npayload = %s\ncontext = %s" % (update_state, payload, user_context) )
    #TWIN_CALLBACKS += 1
    #print ( "Total calls confirmed: %d\n" % TWIN_CALLBACKS )


def send_reported_state_callback(status_code, user_context):
    global SEND_REPORTED_STATE_CALLBACKS
    print ( "Confirmation for reported state received with:\nstatus_code = [%d]\ncontext = %s" % (status_code, user_context) )
    #SEND_REPORTED_STATE_CALLBACKS += 1
    #print ( "    Total calls confirmed: %d" % SEND_REPORTED_STATE_CALLBACKS )


def device_method_callback(method_name, payload, user_context):
    global METHOD_CALLBACKS
    print ( "\nMethod callback called with:\nmethodName = %s\npayload = %s\ncontext = %s" % (method_name, payload, user_context) )
    METHOD_CALLBACKS += 1
    print ( "Total calls confirmed: %d\n" % METHOD_CALLBACKS )
    device_method_return_value = DeviceMethodReturnValue()
    device_method_return_value.response = "{ \"Response\": \"This is the response from the device\" }"
    device_method_return_value.status = 200
    return device_method_return_value


def blob_upload_conf_callback(result, user_context):
    global BLOB_CALLBACKS
    print ( "Blob upload confirmation[%d] received for message with result = %s" % (user_context, result) )
    BLOB_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % BLOB_CALLBACKS )

def iothub_client_init():
    # prepare iothub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    if client.protocol == IoTHubTransportProvider.HTTP:
        client.set_option("timeout", TIMEOUT)
        client.set_option("MinimumPollingTime", MINIMUM_POLLING_TIME)
    # set the time until a message times out
    client.set_option("messageTimeout", MESSAGE_TIMEOUT)
    # some embedded platforms need certificate information
    set_certificates(client)
    # to enable MQTT logging set to 1
    if client.protocol == IoTHubTransportProvider.MQTT:
        client.set_option("logtrace", 0)
    client.set_message_callback(
        receive_message_callback, RECEIVE_CONTEXT)
    if client.protocol == IoTHubTransportProvider.MQTT:
        client.set_device_twin_callback(
            device_twin_callback, TWIN_CONTEXT)
        client.set_device_method_callback(
            device_method_callback, METHOD_CONTEXT)
    return client

def usage():
    print ( "Usage: IoTHubDemo.py -p <protocol> -c <connectionstring>" )
    print ( "    protocol        : <amqp, amqp_ws, http, mqtt, mqtt_ws>" )
    print ( "    connectionstring: <HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>>" )

def main():
	print "Raspberry Pi Azure IoT Hub Demo program\n"

	try:
		client = iothub_client_init()
		print "Client setup..."
		if client.protocol == IoTHubTransportProvider.MQTT:
			print ( "IoTHubClient is reporting state" )
			reported_state = "{\"newState\":\"standBy\"}"
			client.send_reported_state(reported_state, len(reported_state), send_reported_state_callback, SEND_REPORTED_STATE_CONTEXT)
        	print "Starting Loop..."
	        while True:
                	result = read_dht11_dat()
	                if result:
        	                humidity, temperature = result
                	        print "humidity: %s %%,  Temperature: %s C`" % (humidity, temperature)
				msg_txt_formatted = MSG_TXT % (temperature, humidity)
				print msg_txt_formatted
				message = IoTHubMessage(bytearray(msg_txt_formatted, 'utf8'))
				client.send_event_async(message, send_confirmation_callback, 1)
				# Wait for Commands or exit
            
				print ( "Waiting for next reading, press Ctrl-C to exit" )
                		time.sleep(60)
			else:
				time.sleep(1)
				# Wait for Commands or exit
            
				print ( "Waiting for next reading, press Ctrl-C to exit" )

	except IoTHubError as iothub_error:
		print ( "Unexpected error %s from IoTHub" % iothub_error )
		return
	except KeyboardInterrupt:
		print ( "IoTHubClient sample stopped" )

def destroy():
        GPIO.cleanup()

if __name__ == '__main__':
        try:
        	(CONNECTION_STRING, PROTOCOL) = get_iothub_opt(sys.argv[1:], CONNECTION_STRING, PROTOCOL)
    	except OptionError as option_error:
        		print ( option_error )
        		usage()
			destroy()
        		sys.exit(1)

    	print ( "Starting the Raspberry Pi Azure IoT Hub Demo program..." )
    	print ( "    Protocol %s" % PROTOCOL )
    	print ( "    Connection string=%s" % CONNECTION_STRING )
        
	main()
