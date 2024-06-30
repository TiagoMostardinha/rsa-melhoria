import threading
import random


class Streets:
    edges: dict
    graph: dict
    finished: bool
    obu_threads: list
    rsu_threads: list
    car_positions: dict
    stations_location: dict
    connected_to: dict
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
        # TODO: Missing semaphore
        # TODO: send connected_to from rsu or obu
        pass

    def check_ranges(self, id):
        # TODO: Missing semaphore
        # TODO: check if the current id has connection to anyone
        pass

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
        
        # TODO:Missing connected to

        return {
            "edges": edges_info,
            "graph": graph_info,
            "finished": self.finished,
            "car_positions": car_info,
            "stations_location": stations_info,
            "connected_to": self.connected_to
        }


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

    def get_speed_semaphore(self, id, speed, semaphore):
        # TODO: Missing semaphore
        # TODO: get speed based on some algorithm
        pass

    def get_location(self, current_street, position):
        return self.graph[current_street][position]

    def get_path(self, id, current_edge, destination_location):
        # TODO: Missing semaphore
        # TODO: get path with some algorithm
        pass
