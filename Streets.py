import threading


class Streets:
    graph: dict
    finished: bool
    obu_threads: list
    rsu_threads: list
    positions: dict
    connected_to: dict
    semaphore: threading.Semaphore

    def __init__(self,graph):
        self.graph = graph
        self.finished = False
        self.obu_threads = []
        self.rsu_threads = []
        self.positions = {}
        self.connected_to = {}
        self.semaphore = threading.Semaphore()

    def set_initial_position(self, id, position):
        # TODO: Missing semaphore
        self.positions[id] = position

    def get_next_position_and_location(self, id):
        # TODO: Missing semaphore
        # TODO: Implement the function that returns the next position of the car
        pass

    def has_finished(self):
        # TODO: Missing semaphore
        return self.finished

    def set_finished(self):
        # TODO: Missing semaphore
        self.finished = True

    def set_connected_to(self, id, connected_to):
        # TODO: Missing semaphore
        # TODO: send connected_to from rsu or obu
        pass

    def is_on_edge(self,id,position):
        # TODO: Missing semaphore
        # TODO: check if current Car is on a edge
        pass

    def change_edge(self,id,current_edge):
        # TODO: Missing semaphore
        # TODO: check which is the successor edge
        pass

    def check_ranges(self,id):
        # TODO: Missing semaphore
        # TODO: check if the current id has connection to anyone
        pass

    def get_speed_semaphore(self,id,speed,semaphore):
        # TODO: Missing semaphore
        # TODO: get speed based on some algorithm
        pass        

    def get_path(self,id,current_edge,destination_location):
        # TODO: Missing semaphore
        # TODO: get path with some algorithm
        pass