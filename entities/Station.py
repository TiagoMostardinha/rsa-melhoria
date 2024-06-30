import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from Streets import Streets


class Station:
    streets_region: Streets
    name: str
    id: int
    address: str
    mac: str
    location: tuple
    connected_to: list
    old_connected_to: list

    def __init__(self, streets_region, name, id, address, mac, location):
        self.name = name
        self.id = id
        self.address = address
        self.mac = mac
        self.location = location
        self.connected_to = []
        self.old_connected_to = []
        self.streets_region = streets_region

    def start(self):
        client = mqtt.Client(self.name)
        client.on_message = self.on_message
        client.connect(self.address, 1883, 60)
        client.subscribe(topic=[("vanetza/out/cam", 0)])
        client.subscribe(topic=[("vanetza/out/spatem", 0)])
        client.loop_start()

        self.streets_region.set_initial_station(self)

        while not self.streets_region.has_finished():
            pass

        client.loop_stop()
        client.disconnect()
    
    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode('utf-8'))
        msg_type = msg.topic

        if msg_type == 'vanetza/out/cam':
            print("STATION ",self.id,":\t",message)
