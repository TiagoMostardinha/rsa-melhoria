from Streets import Streets
import threading
from entities.Car import Car
from entities.Station import Station


def app():
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

    dir_coordinates = "./coordinates/"
    # TODO: missing importing the coordinates

    # TODO: remove this
    graph = {
        (0, 2): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        (1, 0): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        (1, 3): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        (2, 0): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        (2, 3): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        (2, 4): [0, 1, 2, 3, 4],
        (3, 1): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        (3, 5): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        (4, 2): [0, 1, 2, 3, 4],
        (4, 6): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        (5, 1): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        (5, 6): [0, 1, 2, 3, 4],
        (6, 4): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        (6, 5): [0, 1, 2, 3, 4]
    }

    # Create Streets Shared Region
    streets_region = Streets(graph)

    # Creating obu threads
    obu_list : list[Car]= []

    # TODO:missing random edge and random position
    obu_list.append(Car(streets_region, "obu1", 1,"10.10.10.1", "1:1:1:1:1:1", 0, 0))
    obu_list.append(Car(streets_region, "obu2", 2,"10.10.10.2", "2:2:2:2:2:2", 0, 1))
    obu_list.append(Car(streets_region, "obu3", 3,"10.10.10.3", "3:3:3:3:3:3", 0, 2))

    # Creating rsu threads
    rsu_list : list[Station]= []

    rsu_list.append(Station(streets_region, "rsu1", 4,"10.10.10.4", "4:4:4:4:4:4", (40.637727, -8.656250)))
    rsu_list.append(Station(streets_region, "rsu2", 5,"10.10.10.5", "5:5:5:5:5:5", (40.637148, -8.657087)))

    # Starting rsu and obu threads
    rsu_threads : list[threading.Thread] = []
    obu_threads : list[threading.Thread] = []

    for i in range(len(rsu_list)):
        rsu_threads.append(threading.Thread(target=rsu_threads[i].start))
        rsu_threads[i].start()

    for i in range(len(obu_list)):
        obu_threads.append(threading.Thread(target=obu_list[i].start))
        obu_threads[i].start()

    for i in range(len(rsu_list)):
        rsu_threads[i].join()

    for i in range(len(obu_list)):
        obu_threads[i].join()



if __name__ == '__main__':
    app()
