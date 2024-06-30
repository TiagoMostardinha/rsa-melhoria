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
        self.streets_region.set_initial_station(self)
