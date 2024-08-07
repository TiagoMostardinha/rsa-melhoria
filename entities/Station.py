from Streets import Streets
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import time
import random
import geopy.distance
from protocols.CAM import CAM,SpecialVehicle,PublicTransportContainer
from operator import itemgetter

class Station:
    streets_region: Streets
    name: str
    id: int
    address: str
    mac: str
    location: tuple
    intersections: dict
    range:int
    connected_to: dict[dict]
    street_semaphore : dict[int]
    old_connected_to: dict

    def __init__(self, streets_region, name, id, address, mac, location,intersections,range):
        self.name = name
        self.id = id
        self.address = address
        self.mac = mac
        self.location = location
        self.intersections = intersections
        self.range = range
        self.connected_to = {}
        self.street_semaphore = {}
        self.old_connected_to = {}
        self.streets_region = streets_region

        '''
        semaphore:
        0 = green
        1 = yellow
        2 = red
        '''
        for _,pair_street in self.intersections.items():
            self.street_semaphore[pair_street[0]] = 0
            self.street_semaphore[pair_street[1]] = 0



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

            self.set_semaphore_to_streets()

            self.send_spatem()

            self.set_station_info_in_region()

        client.loop_stop()
        client.disconnect()

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode('utf-8'))
        msg_type = msg.topic

        if msg_type == 'vanetza/out/cam':
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

    def distance_station_to_car(self):
        closest_to_edge = {}

        for edge,_ in self.intersections.items():
            closest_to_edge[edge] = []
            edge_location = self.streets_region.get_edge_location(edge)

            for car_id,msg in self.connected_to.items():
                distance = geopy.distance.distance(edge_location, (msg["latitude"],msg["longitude"])).m

                if distance <= self.range:
                    closest_to_edge[edge].append((car_id,distance))

            closest_to_edge[edge] = sorted(closest_to_edge[edge], key=itemgetter(1))
        return closest_to_edge

    def set_semaphore_to_streets(self):
        closest_to_edge = self.distance_station_to_car()

        closest_to_edge_from_different_street = {}
        for edge,cars_in_range in closest_to_edge.items():
            car_from_different_street = {}

            if not cars_in_range:
                continue

            for car in cars_in_range:
                street = self.streets_region.get_car_street(car[0])

                if street in self.intersections[edge]:
                    car_from_different_street[street] = car

                if len(car_from_different_street.keys()) >= 2:
                    break
            closest_to_edge_from_different_street[edge] = car_from_different_street
        
        for edge,car_from_different_street in closest_to_edge_from_different_street.items():
            streets = self.intersections[edge]

            if not car_from_different_street:
                self.street_semaphore[streets[0]] = 0
                self.street_semaphore[streets[1]] = 0
                continue
            
            if len(car_from_different_street.keys()) == 1:
                self.street_semaphore[streets[0]] = 0
                self.street_semaphore[streets[1]] = 0
                continue

            if car_from_different_street[streets[0]][1] < 30 and car_from_different_street[streets[1]][1] < 30:
                if (car_from_different_street[streets[0]][1] - car_from_different_street[streets[1]][1]) < -30:
                    self.street_semaphore[streets[0]] = 0
                    self.street_semaphore[streets[1]] = 1
                elif (car_from_different_street[streets[0]][1] - car_from_different_street[streets[1]][1]) > 30:
                    self.street_semaphore[streets[0]] = 1
                    self.street_semaphore[streets[1]] = 0
                else:
                    if car_from_different_street[streets[0]][1] < car_from_different_street[streets[1]][1]:
                        self.street_semaphore[streets[0]] = 0
                        if car_from_different_street[streets[1]][1] > 10:
                            self.street_semaphore[streets[1]] = 1
                        else:
                            self.street_semaphore[streets[1]] = 2
                    else:
                        if car_from_different_street[streets[0]][1] > 10:
                            self.street_semaphore[streets[0]] = 1
                        else:
                            self.street_semaphore[streets[1]] = 2
            else:
                self.street_semaphore[streets[0]] = 0
                self.street_semaphore[streets[1]] = 0


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
    
    def send_spatem(self):
        spatem={
            "intersections":[
                {
                    "id":{
                        "id":self.id
                    },
                    "revision":1,
                    "states":[
                        
                    ],
                    "status":{
                        "failureFlash": False,
                        "failureMode": False,
                        "fixedTimeOperation": False,
                        "manualControlIsEnabled": False,
                        "noValidMAPisAvailableAtThisTime": False,
                        "noValidSPATisAvailableAtThisTime": False,
                        "off": False,
                        "preemptIsActive": False,
                        "recentChangeInMAPassignedLanesIDsUsed": False,
                        "recentMAPmessageUpdate": False,
                        "signalPriorityIsActive": False,
                        "standbyOperation": False,
                        "stopTimeIsActivated": False,
                        "trafficDependentOperation": False
                    }

                }
            ]
        }

        for street,semaphore in self.street_semaphore.items():
            spatem["intersections"][0]["states"].append(
                {
                    "signalGroup":int(f"{street[0]}{street[1]}"),
                    "state-time-speed":[
                        {
                            "eventState":semaphore,
                            "timing":{
                                "minEndTime":7
                            }
                        }
                    ]
                }
            )
        
        publish.single('vanetza/in/spatem', json.dumps(spatem), hostname=self.address)


    def set_station_info_in_region(self):
        intersections_info = {}
        for key,value in self.intersections.items():
            intersections_info[key] = []
            for v in value:
                intersections_info[key].append(list(v))


        street_semaphore_info = {}
        for key,value in self.street_semaphore.items():
            street_semaphore_info[str(key)] = value


        info = {
            "name" :            self.name,
            "id":               self.id,
            "location":         list(self.location),
            "intersections":    intersections_info,
            "range":            self.range,
            "street_semaphore": street_semaphore_info,
            "connected_to":     self.connected_to
        }

        self.streets_region.set_station_info(self.id,info)