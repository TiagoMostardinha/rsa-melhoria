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
    position: int
    location: tuple
    semaphore: int
    last_received_cam: time
    last_received_spatem: time
    connected_to: list
    old_connected_to: list
    current_edge: int
    next_edge: int


    def __init__(self,streets_region, name, id, address, mac, position, current_edge):
        self.name = name
        self.id = id
        self.address = address
        self.mac = mac
        self.length = 5
        self.width = 2
        self.speed = 0
        self.position = position
        self.location = ()
        self.semaphore = 0
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
        self.current_edge = current_edge
        self.next_edge = -1
        self.streets_region = streets_region

    def start(self):
        # TODO: Implement the start thread of the car
        pass
