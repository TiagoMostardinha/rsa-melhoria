import random
import time
from Streets import Streets


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
        self.speed = 0
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

        self.streets_region.set_initial_car(self)

        while not self.streets_region.has_finished():
            self.streets_region.get_next_position_and_location(self.id)

            print("Car[", self.id, "]: street=", self.current_street,
                  " pos=", self.position, " loc=", self.location)
            time.sleep(1 + random.random())
