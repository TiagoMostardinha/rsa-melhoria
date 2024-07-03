import threading
import random
import geopy.distance
import subprocess


class Streets:
    edges: dict
    graph: dict
    finished: bool
    obu_threads: list
    rsu_threads: list
    car_positions: dict
    stations_location: dict
    connected_to: dict
    station_network: dict
    station_info: dict
    car_info:dict
    access: threading.Semaphore

    def __init__(self, edges, graph):
        self.edges = edges
        self.graph = graph
        self.finished = False
        self.obu_threads = [None] * 10
        self.rsu_threads = [None] * 10
        self.car_positions = {}
        self.stations_location = {}
        self.connected_to = {}
        self.station_network = {}
        self.station_info = {}
        self.car_info = {}
        self.access = threading.Semaphore()

################## synchronized methods ##################

    def set_initial_car(self, car):
        self.access.acquire()
        self.car_positions[car.id] = (car.current_street, car.position,self.get_location(car.current_street,car.position))
        self.obu_threads[car.id] = car
        self.access.release()

    def set_initial_station(self, station):
        self.access.acquire()
        self.stations_location[station.id] = station.location
        self.station_network[station.id] = {}
        self.rsu_threads[station.id] = station
        self.access.release()

    def get_next_position_and_location(self, id):
        self.access.acquire()
        car = self.obu_threads[id]

        if id not in self.car_positions:
            self.access.release()
            return None

        current_street, position,_ = self.car_positions[id]

        if self.is_on_edge(current_street, position + 1):
            current_street, position = self.change_street(car)
        else:
            position += 1

        location = self.get_location(current_street, position)

        self.car_positions[id] = (current_street, position,location)

        car.position = position
        car.current_street = current_street
        car.location = location

        self.access.release()

    def set_finished(self):
        self.access.acquire()
        self.finished = True
        self.access.release()

    def set_connected_to(self, id, connected_to):
        self.access.acquire()
        self.connected_to[id] = connected_to
        self.access.release()

    def check_ranges(self, id,range):
        self.access.acquire()

        station_coord = self.stations_location[id]

        in_range_cars = {}

        for car_id,car_info in self.car_positions.items():
            car_coord = car_info[2]
            if station_coord != [] and car_coord != []:
                distance = geopy.distance.distance(station_coord, car_coord).m
                if distance < range:
                    in_range_cars[car_id] = True
                else:
                    in_range_cars[car_id] = False
            else:
                in_range_cars[car_id] = False
        
        self.config_station_network(id,in_range_cars)


        self.access.release()

    def choose_next_street(self, id):
        self.access.acquire()
        car = self.obu_threads[id]
        current_street = car.current_street

        possible_street = []
        for street in self.graph.keys():
            if current_street[1] == street[0]:
                possible_street.append(street)

        i_next_street = int(random.random() * len(possible_street))
        car.next_street = possible_street[i_next_street]

        self.access.release()
    
    def get_car_street(self,car_id):
        self.access.acquire()
        street = self.car_positions[car_id][0]
        self.access.release()
        return street
    
    def get_edge_location(self,edge):
        self.access.acquire()
        location = self.edges[edge]
        self.access.release()
        return location
    
    def get_info(self):
        edges_info = {}
        for key,value in self.edges.items():
            edges_info[key] = list(value)
        
        graph_info = {}
        for key,value in self.graph.items():
            graph_info[str(key)] = value
        
        car_info = {}
        for key,value in self.car_positions.items():
            car_info[key] = list(value)
        
        stations_info = {}
        for key,value in self.stations_location.items():
            stations_info[key] = list(value)

        msg = {
            "edges": edges_info,
            "graph": graph_info,
            "finished": self.finished,
            "car_positions": car_info,
            "stations_location": stations_info,
            "connected_to": self.connected_to,
            "station_info":list(self.station_info.values()),
            "car_info":list(self.car_info.values())
        }

        return msg

    def set_station_info(self,id,info):
        self.access.acquire()
        self.station_info[id] = info
        self.access.release()
    
    def set_car_info(self,id,info):
        self.access.acquire()
        self.car_info[id] = info
        self.access.release()


################## private methods ##################

    def has_finished(self):
        return self.finished

    def is_on_edge(self, current_street, position):
        if position >= len(self.graph[current_street]):
            return False

        coords = self.get_location(current_street, position)

        if coords in self.edges.values():
            return True

        return False

    def change_street(self,car):
        if car.next_street != ():
            car.current_street = car.next_street
            car.position = 0
            car.next_street = ()
        return car.current_street, car.position

    def get_location(self, current_street, position):
        return self.graph[current_street][position]
    
    def config_station_network(self,id,in_range_cars:dict):
        station_name = self.rsu_threads[id].name
        station_mac = self.rsu_threads[id].mac

        for car_id,is_near in in_range_cars.items():
            car_name = self.obu_threads[car_id].name
            car_mac = self.obu_threads[car_id].mac

            try:
                if not self.station_network[id] or self.station_network[id][car_id] != is_near:
                    if is_near:
                        subprocess.run(f"docker compose exec {station_name} unblock {car_mac}", shell=True, check=True)
                        subprocess.run(f"docker compose exec {car_name} unblock {station_mac}", shell=True, check=True)
                    else:
                        subprocess.run(f"docker compose exec {station_name} block {car_mac}", shell=True, check=True)
                        subprocess.run(f"docker compose exec {car_name} block {station_mac}", shell=True, check=True)
            except Exception:
                continue
        
        self.station_network[id] = in_range_cars