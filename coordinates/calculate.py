from geopy.distance import geodesic, great_circle

n = 10
name = "./coordinates/street13.txt"


point1 = (40.63749489056348,-8.655980723580765)
point2 = (40.63700365712481,-8.656638840379339)

geodesic_distance = geodesic(point1, point2).m

great_circle_distance = great_circle(point1, point2).m

# print(f"Geodesic distance: {geodesic_distance} m")
# print(f"Great-circle distance: {great_circle_distance} m")

vector = ((point2[0] - point1[0])/(n-1), (point2[1] - point1[1])/(n-1))

coordinates = []
# coordinates.append(point1)
for i in range(n-1):
    coordinates.append((point1[0] + i*vector[0], point1[1] + i*vector[1]))

coordinates.append(point2)


with open(name, "w") as f:
    for c in coordinates:
        f.write(f"{c[0]},{c[1]}\n")
