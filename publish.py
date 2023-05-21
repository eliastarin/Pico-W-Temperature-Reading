import network
import time
import machine
import onewire
from umqtt.simple import MQTTClient
from machine import Pin
led = Pin('LED',Pin.OUT)

# Set up the OneWire bus on GPIO pin 4
ow = onewire.OneWire(machine.Pin(4))

# Search for any DS18B20 temperature sensors on the bus
devices = ow.scan()
if len(devices) == 0:
    print("No DS18B20 devices found")
else:
    print("Found DS18B20 device(s) at:", devices)


# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = "Boekenroodegast"
wifi_password = "Welkom@Boekenroode27"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)

while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to WiFi")

# Fill in your Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = "io.adafruit.com"
mqtt_username = "domnulelias"  # Your Adafruit IO username
mqtt_password = "aio_zCbG39OjTQkGLPXs5w0b9GGGWDwh"  # Adafruit IO Key
mqtt_publish_topic = "domnulelias/feeds/delta-t"  # The MQTT topic for your Adafruit IO Feed
# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = "escherinthepalace"

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password)

mqtt_client.connect()
# -----------------------------------------------------------------------------------------------------------------------
# Publish a data point to the Adafruit IO MQTT server every 3 seconds
try:
    while True:
        led.toggle()
        ow.reset()
        ow.writebyte(0xCC)  # Skip ROM command
        ow.writebyte(0x44)  # Start temperature conversion
        time.sleep_ms(750)  # Wait for conversion to complete

        ow.reset()
        ow.writebyte(0xCC)  # Skip ROM command
        ow.writebyte(0xBE)  # Read temperature
        data = bytearray(9)
        ow.readinto(data)

        # Parse the temperature data
        temp_raw = (data[1] << 8) | data[0]
        temp_celsius = temp_raw / 16.0
        # Publish the data to the topic!
        mqtt_client.publish(mqtt_publish_topic, str(temp_celsius)) 
        # Delay a bit to avoid hitting the rate limit
        time.sleep(3)
# -----------------------------------------------------------------------------------------------------------------------        
except Exception as e:
    print(f'Failed to publish message: {e}')
finally:
    mqtt_client.disconnect()