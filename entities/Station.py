from Streets import Streets
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import time
from protocols.CAM import CAM,SpecialVehicle,PublicTransportContainer

class Station:
    streets_region: Streets
    name: str
    id: int
    address: str
    mac: str
    location: tuple
    range:int
    connected_to: dict[dict]
    old_connected_to: dict

    def __init__(self, streets_region, name, id, address, mac, location,range):
        self.name = name
        self.id = id
        self.address = address
        self.mac = mac
        self.location = location
        self.range = range
        self.connected_to = {}
        self.old_connected_to = {}
        self.streets_region = streets_region

    def start(self):
        self.streets_region.set_initial_station(self)
        self.streets_region.check_ranges(self.id,self.range)

        time.sleep(1)

        client = mqtt.Client(self.name)
        client.on_message = self.on_message
        client.connect(self.address, 1883, 60)
        client.subscribe(topic=[("vanetza/out/cam", 0)])
        client.subscribe(topic=[("vanetza/out/spatem", 0)])
        client.loop_start()

        while not self.streets_region.has_finished():
            self.streets_region.check_ranges(self.id,self.range)

            time.sleep(0.5)

            #self.send_cam()

            self.check_validity(client)

        client.loop_stop()
        client.disconnect()

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode('utf-8'))
        msg_type = msg.topic

        if msg_type == 'vanetza/out/cam':
            # TODO: Implement the logic for the CAM message, stationID, timestamp, latitude, longitude, speed
            new_cam = {
                'timestamp': message['timestamp'],
                'stationID': message['stationID'],
                'latitude': message['latitude'],
                'longitude': message['longitude'],
                'speed': message['speed']
            }

            if new_cam['stationID'] not in self.connected_to:
                try:
                    self.connected_to[new_cam['stationID']] = new_cam
                except Exception:
                    pass

            if new_cam['timestamp'] > self.connected_to[new_cam['stationID']]['timestamp']:
                self.connected_to[new_cam['stationID']] = new_cam

            self.streets_region.set_connected_to(self.id, self.connected_to)

        # TODO: SPATEM

    def check_validity(self,client):
        client.loop_stop()

        if not self.connected_to:
            client.loop_start()
            return

        connected_to_items = self.connected_to.copy()
        for key, msg in connected_to_items.items():
            if (time.time() - msg['timestamp']) > 2:
                try:
                    self.old_connected_to[key] = msg
                    self.connected_to.pop(key,None)
                except Exception:
                    continue

        
        self.streets_region.set_connected_to(self.id, self.connected_to)
        client.loop_start()

    def send_cam(self):
        cam_message = CAM(
            False,
            0,
            0,
            0,
            False,
            False,
            False,
            0,
            "UNAVAILABLE",
            False,
            False,
            0,
            0,
            self.location[0],
            0,
            self.location[1],
            0,
            0,
            0,
            SpecialVehicle(PublicTransportContainer(False)),
            0,
            0,
            False,
            self.id,
            5,
            0,
            0,
        )
        msg = CAM.to_dict(cam_message)
        publish.single('vanetza/in/cam', json.dumps(msg), hostname=self.address)