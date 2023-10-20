import time
from paho.mqtt import client as client_mqtt
import serial
import os
from dotenv import load_dotenv 
import json


def potential_detection(detected_person):
    detection = True
    for i in range(0, len(detected_person) - 2):
        if detected_person[i+1] > 0.8*detected_person[i]:
            detection = False
    return detection


load_dotenv()

serial_port = os.environ['SERIAL_PORT']
host = os.environ['HOST']
client_id = os.environ['CLIENT_MQTT']
client_android = os.environ['CLIENT_ANDROID']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
asset_id = os.environ['ASSET_ID']
publish_topic = os.environ['PUBLISH_TOPIC']
temperature_topic = os.environ['TEMPERATURE_TOPIC']
pressure_topic = os.environ['PRESSURE_TOPIC']
proximity_topic = os.environ['PROXIMITY_TOPIC']
motion_topic = os.environ['MOTION_TOPIC']
accX_topic = os.environ['ACCELERATION_X_TOPIC']
accY_topic = os.environ['ACCELERATION_Y_TOPIC']
accZ_topic = os.environ['ACCELERATION_Z_TOPIC']
gyroX_topic = os.environ['GYROSCOPE_X_TOPIC']
gyroY_topic = os.environ['GYROSCOPE_Y_TOPIC']
gyroZ_topic = os.environ['GYROSCOPE_Z_TOPIC']
red_topic = os.environ['COLOR_RED_TOPIC']
blue_topic = os.environ['COLOR_BLUE_TOPIC']
green_topic = os.environ['COLOR_GREEN_TOPIC']
alpha_topic = os.environ['COLOR_ALPHA_TOPIC']
android_topic = os.environ['ANDROID_TOPIC']
temperature_low_alarm_topic = os.environ['TEMPERATURE_LOW_ALARM']
temperature_high_alarm_topic = os.environ['TEMPERATURE_HIGH_ALARM']
pressure_alarm_topic = os.environ['PRESSURE_ALARM']
brightness_alarm_topic = os.environ['BRIGHTNESS_ALARM']
notification_alarm_topic = os.environ['NOTIFICATION_ALARM']

ser = serial.Serial(serial_port, timeout=1)

temperature_list = list()
pressure_list = list()
proximity_list = list()
red_list = list()
green_list = list()
blue_list = list()
alpha_list = list()
aX_list = list()
aY_list = list()
aZ_list = list()
gX_list = list()
gY_list = list()
gZ_list = list()
detected_person = list()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Failed to connect to MQTT broker")


def on_disconnect(client, userdata, rc):
    print('disconnecting reason ' + str(rc))
    client.disconnected_flag = True
    client.connected_flag = False


def on_publish(client, userdata, result):
    print('data published \n')
    pass

def on_subscribe(clientSubscribe, userdata, mid, granted_qos):
    print("subscribed ", str(mid))

def on_message(client, userdata, message):
    print("message received ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)


client_mqtt.Client.connected_flag = False
client = client_mqtt.Client(client_id)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username, password)

client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_disconnect = on_disconnect

print('Clients are connecting to broker')
client.connect(host, port=1883, keepalive=60, bind_address="")

time_last = time.time()

try:
    while True:
        s = ser.readline().decode()
        if s != "":
            rows = [float(x) for x in s.split(',')]
            time_current = time.time()
            # print(rows)

            temperature = rows[0]
            pressure = rows[1]
            proximity = rows[2]
            red = rows[3]
            green = rows[4]
            blue = rows[5]
            alpha = rows[6]
            aX = rows[7]
            aY = rows[8]
            aZ = rows[9]
            gX = rows[10]
            gY = rows[11]
            gZ = rows[12]
    
            temperature_list.append(temperature)
            pressure_list.append(pressure)
            proximity_list.append(proximity)
            red_list.append(red)
            green_list.append(green)
            blue_list.append(blue)
            alpha_list.append(alpha)
            aX_list.append(aX)
            aY_list.append(aY)
            aZ_list.append(aZ)
            gX_list.append(gX)
            gY_list.append(gY)
            gZ_list.append(gZ)

            if int(time_current - time_last) >= 2:
                avgTemperature = sum(temperature_list) / len(temperature_list)
                avgPressure = sum(pressure_list) / len(pressure_list)
                avgProximity = sum(proximity_list) / len(proximity_list)
                avgRed = sum(red_list) / len(red_list)
                avgGreen = sum(green_list) / len(green_list)
                avgBlue = sum(blue_list) / len(blue_list)
                avgAlpha = sum(alpha_list) / len(alpha_list)
                avgAx = sum(aX_list) / len(aX_list)
                avgAy = sum(aY_list) / len(aY_list)
                avgAz = sum(aZ_list) / len(aZ_list)
                avgGx = sum(gX_list) / len(gX_list)
                avgGy = sum(gY_list) / len(gY_list)
                avgGz = sum(gZ_list) / len(gZ_list)
                motion_data = {
                    "aX": round(avgAx, 2),
                    "aY": round(avgAy, 2),
                    "aZ": round(avgAz, 2),
                    "gX": round(avgGx, 2),
                    "gY": round(avgGy, 2),
                    "gZ": round(avgGz, 2)
                }
                client.publish(publish_topic + temperature_topic + asset_id, round(avgTemperature, 2))
                client.publish(publish_topic + pressure_topic + asset_id, round(avgPressure, 2))
                client.publish(publish_topic + proximity_topic + asset_id, round(avgProximity))
                client.publish(publish_topic + red_topic + asset_id, round(avgRed))
                client.publish(publish_topic + green_topic + asset_id, round(avgGreen))
                client.publish(publish_topic + blue_topic + asset_id, round(avgBlue))
                client.publish(publish_topic + alpha_topic + asset_id, round(avgAlpha))
                client.publish(publish_topic + motion_topic + asset_id, json.dumps(motion_data))
                #for creating motion insigths only
                client.publish(publish_topic + accX_topic + asset_id, motion_data['aX'])
                client.publish(publish_topic + accY_topic + asset_id, motion_data['aY'])
                client.publish(publish_topic + accZ_topic + asset_id, motion_data['aZ'])
                client.publish(publish_topic + gyroX_topic + asset_id, motion_data['gX'])
                client.publish(publish_topic + gyroY_topic + asset_id, motion_data['gY'])
                client.publish(publish_topic + gyroZ_topic + asset_id, motion_data['gZ'])

                if round(avgProximity) < 128:
                    detected_person.append(round(avgProximity))

                if len(detected_person) == 5 and potential_detection(detected_person):
                    client.publish(publish_topic + notification_alarm_topic + asset_id, "true")
                    detected_person.clear()
                else:
                    client.publish(publish_topic + notification_alarm_topic + asset_id, "false")

                temperature_list.clear()
                pressure_list.clear()
                proximity_list.clear()
                red_list.clear()
                green_list.clear()
                blue_list.clear()
                alpha_list.clear()
                aX_list.clear()
                aY_list.clear()
                aZ_list.clear()
                gX_list.clear()
                gY_list.clear()
                gZ_list.clear()

                time_last = time.time()

            
except KeyboardInterrupt:
    print("Disconnecting")
    client.disconnect()