import time
import ttn
import csv
import sys

from itertools import chain

app_id = "app_lora_coverage_analyzer"
access_key = "ttn-account-v2.g98qkQPAsfJAHqmClm8vNQtl7d4_k_IF_fI5X0-N0iM"

def uplink_callback(msg, client):
  print("Received uplink from ", msg.dev_id)
  #print(msg)
  print("dev_lattitude : ", msg.payload_fields.lattitude, 
        ", dev_longitude : ", msg.payload_fields.longitude, 
        ", rssi : ", msg.payload_fields.rssi, 
        ", snr : ", msg.payload_fields.snr,
        ", gw_lattitude : ", msg.metadata.gateways[0].latitude,
        ", gw_longitude : ", msg.metadata.gateways[0].longitude)

  if msg.payload_fields.lattitude != '-1' and msg.payload_fields.longitude != '-1':
      with open('lca_data.csv', 'a+') as csvf:
        filewriter = csv.writer(csvf)
        filewriter.writerow([ msg.payload_fields.lattitude, 
                              msg.payload_fields.longitude, 
                              msg.payload_fields.rssi, 
                              msg.payload_fields.snr,
                              msg.metadata.gateways[0].latitude,
                              msg.metadata.gateways[0].longitude])
      csvf.close()

def connection_setup(app_id, access_key, uplink_callback):
  handler = ttn.HandlerClient(app_id, access_key)

  mqtt_client = handler.data()
  mqtt_client.set_uplink_callback(uplink_callback)
  mqtt_client.connect()

with open('lca_data.csv', 'w') as csvf:
  filewriter = csv.writer(csvf)
  filewriter.writerow(['dev_latitude', 'dev_longitude', 'rssi', 'snr', 'gw_latitude', 'gw_longitude'])
csvf.close()

connection_setup(app_id, access_key, uplink_callback)

handler = ttn.HandlerClient(app_id, access_key)

mqtt_client = handler.data()
mqtt_client.set_uplink_callback(uplink_callback)
mqtt_client.connect()

while True:
  try:
    time.sleep(10)
  except KeyboardInterrupt:
    sys.exit()
  except:
    mqtt_client.close()

    connection_setup(app_id, access_key, uplink_callback)
    handler = ttn.HandlerClient(app_id, access_key)

    mqtt_client = handler.data()
    mqtt_client.set_uplink_callback(uplink_callback)
    mqtt_client.connect()
    continue

  