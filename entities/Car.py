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
        self.last_received_spatem = None
        self.connected_to = []
        self.old_connected_to = []
        self.current_street = current_street
        self.next_street = ()
        self.streets_region = streets_region

        self.location = self.streets_region.get_location(self.current_street,self.position)

    def start(self):
        self.streets_region.set_initial_car(self)

        time.sleep(1)

        client = mqtt.Client(self.name)
        client.on_message = self.on_message
        client.connect(self.address, 1883, 60)
        client.subscribe(topic=[("vanetza/out/cam", 0)])
        client.subscribe(topic=[("vanetza/out/spatem", 0)])
        client.loop_start()

        tick = 0

        while not self.streets_region.has_finished():
            tick += 1
            if self.next_street == ():
                self.streets_region.choose_next_street(self.id)
            

            self.check_validity()

            if self.virt_semaphore == 0:
                self.speed = 1
            elif self.virt_semaphore == 1:
                self.speed = 0.5
            else:
                self.speed = 0


            if self.speed != 0:
                if tick >= (1/self.speed):
                    self.streets_region.get_next_position_and_location(self.id)
                    tick = 0
            else:
                tick = 0

            self.send_cam()

            self.set_car_info_in_region()
            
            # TODO: remove this
            #time.sleep(2)
            time.sleep(2 + random.random())

        client.loop_stop()
        client.disconnect()

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode('utf-8'))
        msg_type = msg.topic

        if msg_type == 'vanetza/out/spatem':
            states = message['fields']['spat']['intersections'][0]['states']

            for lane in states:
                street_str = f"{lane['signalGroup']:02}"
                street = (int(street_str[0]),int(street_str[1]))

                if self.current_street == street:
                    self.virt_semaphore = lane['state-time-speed'][0]['eventState']
                    self.last_received_spatem = message['timestamp']

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

    def check_validity(self):
        if not self.last_received_spatem:
            return
        
        if (time.time() - self.last_received_spatem) > 3:
            self.speed = 1

    def set_car_info_in_region(self):
        info = {
            "name":self.name,
            "id":self.id,
            "speed":self.speed,
            "location":list(self.location),
            "virt_semaphore":self.virt_semaphore
        }

        self.streets_region.set_car_info(self.id,info)