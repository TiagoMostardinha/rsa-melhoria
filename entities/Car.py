import random
import time
from Streets import Streets
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from protocols.CAM import CAM, SpecialVehicle, PublicTransportContainer


class Car:
    streets_region: Streets
    name: str
    id: int
    address: str
    mac: str
    length: int
    width: int
    speed: int
    current_street: tuple
    next_street: tuple
    position: int
    location: tuple
    virt_semaphore: int
    last_received_cam: time
    last_received_spatem: time
    connected_to: list
    old_connected_to: list

    def __init__(self, streets_region, name, id, address, mac, position, current_street):
        self.name = name
        self.id = id
        self.address = address
        self.mac = mac
        self.length = 5
        self.width = 2
        self.speed = 1
        self.position = position
        self.location = ()
        self.virt_semaphore = 0
        '''
        semaphore:
        0 = green
        1 = yellow
        2 = red
        '''
        self.last_received_cam = None
        self.last_received_spatem = None
        self.connected_to = []
        self.old_connected_to = []
        self.current_street = current_street
        self.next_street = ()
        self.streets_region = streets_region

    # TODO: Implement the start thread of the car
    def start(self):
        # TODO: implement mqtt
        client = mqtt.Client(self.name)
        client.on_message = self.on_message
        client.connect(self.address, 1883, 60)
        client.subscribe(topic=[("vanetza/out/cam", 0)])
        client.subscribe(topic=[("vanetza/out/spatem", 0)])
        client.loop_start()

        self.streets_region.set_initial_car(self)

        while not self.streets_region.has_finished():
            if self.next_street == ():
                self.streets_region.choose_next_street(self.id)

            self.streets_region.get_next_position_and_location(self.id)

            self.send_cam()

            # TODO: remove this
            # print("Car[", self.id, "]:\tst=", self.current_street, "\tpos=", self.position, "\tloc=",
            #       self.location)
            time.sleep(self.speed + random.random())

        client.loop_stop()
        client.disconnect()

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode('utf-8'))
        msg_type = msg.topic

        # TODO: Implement the message handling SPATEM

        # if msg_type == 'vanetza/out/spatem':
        #     edges = self.graph.edges()
        #     states = message['fields']['spat']['intersections'][0]['states']

        #     for state in states:
        #         if state['signalGroup'] == edges[self.current_edge]['attr']['signalGroup']:
        #             if state['state-time-speed'][0]['eventState'] == 2:
        #                 self.signal_group = state['state-time-speed'][0]['eventState']

        #                 self.last_received_spatem = message['timestamp']

    # TODO: Implement the message sending CAM

    def send_cam(self):
        cam_message = CAM(
            True,
            0,
            0,
            0,
            False,
            True,
            True,
            0,
            "FOWARD",
            False,
            True,
            0,
            0,
            self.location[0],
            self.length,
            self.location[1],
            0,
            0,
            0,
            SpecialVehicle(PublicTransportContainer(False)),
            float(self.speed),
            0,
            True,
            self.id,
            19,
            self.width,
            0,
        )
        msg = CAM.to_dict(cam_message)
        publish.single('vanetza/in/cam', json.dumps(msg), hostname=self.address)
