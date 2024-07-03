from Streets import Streets
import threading
from entities.Car import Car
from entities.Station import Station
from flask import Flask, render_template, request
import json,subprocess,time,logging
import random

app = Flask(__name__)

# Disable Flask's default logging
log = logging.getLogger('werkzeug')
log.disabled = True

streets_region = None
obu_list : list[Car]= []
rsu_list : list[Station]= []

def init_simulation():
    global streets_region, obu_list, rsu_list

    process = subprocess.Popen("docker compose down", shell=True)
    process.wait()

    process = subprocess.Popen("docker compose up -d", shell=True)
    process.wait()

    time.sleep(2)

    # Create graph
    graph = {
        (0, 2): [],
        (1, 0): [],
        (1, 3): [],
        (2, 0): [],
        (2, 3): [],
        (2, 4): [],
        (3, 1): [],
        (3, 5): [],
        (4, 2): [],
        (4, 6): [],
        (5, 1): [],
        (5, 6): [],
        (6, 4): [],
        (6, 5): []
    }

    edges = {
        0: (),
        1: (),
        2: (),
        3: (),
        4: (),
        5: (),
        6: ()
    }

    # Load coordinates
    dir_coordinates = "./coordinates/"
    for key in graph.keys():
        with open(dir_coordinates + str(key[0]) + "" + str(key[1]) + ".csv", "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line != "":
                    line = line.split(",")
                    graph[key].append((float(line[0]), float(line[1])))
        
        edges[key[0]] = graph[key][0]

    intersections = {
        0 : [(1,0),(2,0)],
        1 : [(3,1),(5,1)],
        2 : [(0,2),(4,2)],
        3 : [(1,3),(2,3)],
        4 : [(2,4),(6,4)],
        5 : [(3,5),(6,5)],
        6 : [(4,6),(5,6)],
    }

    # Create Streets Shared Region
    streets_region = Streets(edges,graph)

    # Creating Cars(obu) and Stations(rsu)
    rsu_range = 60
    isRandom = True

    if isRandom:
        car_street_position = random_street_position(graph,5)

        obu_list.append(Car(streets_region, "obu1", 5,"192.168.98.21", "6e:06:e0:03:00:05", car_street_position[0][0],car_street_position[0][1]))
        obu_list.append(Car(streets_region, "obu2", 6,"192.168.98.22", "6e:06:e0:03:00:06", car_street_position[1][0],car_street_position[1][1]))
        obu_list.append(Car(streets_region, "obu3", 7,"192.168.98.23", "6e:06:e0:03:00:07", car_street_position[2][0],car_street_position[2][1]))
        obu_list.append(Car(streets_region, "obu4", 8,"192.168.98.24", "6e:06:e0:03:00:08", car_street_position[3][0],car_street_position[3][1]))
        obu_list.append(Car(streets_region, "obu5", 9,"192.168.98.25", "6e:06:e0:03:00:09", car_street_position[4][0],car_street_position[4][1]))
    else:
        obu_list.append(Car(streets_region, "obu1", 5,"192.168.98.21", "6e:06:e0:03:00:05", 7,(1,3)))
        obu_list.append(Car(streets_region, "obu2", 6,"192.168.98.22", "6e:06:e0:03:00:06", 7, (2,3)))
        obu_list.append(Car(streets_region, "obu3", 7,"192.168.98.23", "6e:06:e0:03:00:07", 0, (2,3)))
        obu_list.append(Car(streets_region, "obu4", 8,"192.168.98.24", "6e:06:e0:03:00:08", 3, (1,3)))
        obu_list.append(Car(streets_region, "obu5", 9,"192.168.98.25", "6e:06:e0:03:00:09", 4, (2,3)))

    rsu_list.append(Station(streets_region, "rsu1", 1,"192.168.98.11", "6e:06:e0:03:00:01", (40.637983, -8.656642),choose_intersection(intersections,[0]),rsu_range))
    rsu_list.append(Station(streets_region, "rsu2", 2,"192.168.98.12", "6e:06:e0:03:00:02", (40.637285, -8.656363),choose_intersection(intersections,[1,3]),rsu_range))
    rsu_list.append(Station(streets_region, "rsu3", 3,"192.168.98.13", "6e:06:e0:03:00:03", (40.637495, -8.657532),choose_intersection(intersections,[2,4]),rsu_range))
    rsu_list.append(Station(streets_region, "rsu4", 4,"192.168.98.14", "6e:06:e0:03:00:04", (40.636347, -8.655998),choose_intersection(intersections,[5,6]),rsu_range))

    # Starting rsu and obu threads
    rsu_threads : list[threading.Thread] = [threading.Thread(target=rsu.start) for rsu in rsu_list]
    obu_threads : list[threading.Thread] = [threading.Thread(target=obu.start) for obu in obu_list]

    for i in range(len(rsu_list)):
        rsu_threads[i].start()

    for i in range(len(obu_list)):
        obu_threads[i].start()

    for i in range(len(rsu_list)):
        rsu_threads[i].join()

    for i in range(len(obu_list)):
        obu_threads[i].join()

    print("Simulation finished")
    streets_region = None

def random_street_position(graph,n_car) -> dict[tuple]:
    car_street_position = {}
    streets = list(graph.keys())

    for i in range(n_car):
        while True:
            street = streets[random.randint(0,len(streets)-1)]
            position = random.randint(0,len(graph[street])-2)
            
            if (street,position) not in car_street_position.values():
                car_street_position[i] = (position,street)
                break
    
    return car_street_position


def choose_intersection(intersections,edges_to_station:list) -> dict:
    return {k: intersections[k] for k in edges_to_station}

@app.route('/start', methods=['POST'])
def start_simulation():
    init_simulation()
    print("Simulation started")
    return "Simulation started"

@app.route('/stop', methods=['POST'])
def stop_simulation():
    global streets_region
    streets_region.set_finished()
    process = subprocess.Popen("docker compose down", shell=True)
    process.wait()
    streets_region = None
    print("Simulation stopped")
    return "Simulation stopped"

@app.route('/info', methods=['GET'])
def get_info():
    global streets_region
    if streets_region is None:
        return "Simulation not started"
    info = streets_region.get_info()
    return json.dumps(info)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', refresh_rate=100)



if __name__ == '__main__':
    app.run(debug=True)
    
