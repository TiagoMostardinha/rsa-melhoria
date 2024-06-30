from Streets import Streets
import threading
from entities.Car import Car
from entities.Station import Station
from flask import Flask, render_template, request
import json,subprocess,time

app = Flask(__name__)

streets_region = None
obu_list : list[Car]= []
rsu_list : list[Station]= []

def init_simulation():
    global streets_region, obu_list, rsu_list

    # TODO: missing docker
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


    # Create Streets Shared Region
    streets_region = Streets(edges,graph)

    # TODO:missing random edge and random position
    obu_list.append(Car(streets_region, "obu1", 5,"192.168.98.21", "6e:06:e0:03:00:05", 0,(0,2)))
    obu_list.append(Car(streets_region, "obu2", 6,"192.168.98.22", "6e:06:e0:03:00:06", 0, (1,0)))
    obu_list.append(Car(streets_region, "obu3", 7,"192.168.98.23", "6e:06:e0:03:00:07", 0, (1,3)))

    rsu_list.append(Station(streets_region, "rsu1", 1,"192.168.98.11", "6e:06:e0:03:00:01", (40.637727, -8.656250)))
    rsu_list.append(Station(streets_region, "rsu2", 2,"192.168.98.12", "6e:06:e0:03:00:02", (40.637148, -8.657087)))

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

    process = subprocess.Popen("docker compose down", shell=True)
    process.wait()
    print("Simulation finished")

# TODO: atribute a random edge to the car
def random_edge(n_edges) -> int:
    pass


@app.route('/start', methods=['POST'])
def start_simulation():
    init_simulation()
    return "Simulation started"

@app.route('/stop', methods=['POST'])
def stop_simulation():
    streets_region.set_finished()
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
    
