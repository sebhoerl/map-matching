import numpy as np
import pickle
import matplotlib.pyplot as plt
from tqdm import tqdm

with open("data/osm.p", "rb") as f:
    osm_data = pickle.load(f)

with open("data/tomtom.p", "rb") as f:
    tomtom_data = pickle.load(f)

with open("data/matching.p", "rb") as f:
    matching = pickle.load(f)

with open("data/sanitized_validation_matching.p", "rb") as f:
    sanitized_matching = pickle.load(f)

if False:
    plt.figure()

    for tomtom_id, osm_id in tqdm(matching.items()):
    #for tomtom_id, osm_id in sanitized_matching.items():
        #tomtom_id, osm_id = row[1], row[6]
        if not tomtom_id in tomtom_data: continue
        if not osm_id in osm_data: continue

        from_coord, to_coord, _, osm_speed, _ = osm_data[osm_id]
        if osm_speed is None: continue

        plt.plot([from_coord[0], to_coord[0]], [from_coord[1], to_coord[1]], 'b--')

        from_coord, to_coord, _,tomtom_speed, _ = tomtom_data[tomtom_id]
        plt.plot([from_coord[0], to_coord[0]], [from_coord[1], to_coord[1]], 'r-')

    plt.show()

if True:
    plt.figure()

    aggregated = {}
    n = 0

    #for tomtom_id, osm_id in tqdm(matching.items()):
    for tomtom_id, osm_id in sanitized_matching.items():
        #tomtom_id, osm_id = row[1], row[6]
        osm_speed = osm_data[osm_id][3]
        tomtom_speed = tomtom_data[tomtom_id][3]

        osm_class = osm_data[osm_id][2]
        tomtom_class = tomtom_data[tomtom_id][2]

        #print(osm_data[osm_id][2], tomtom_data[tomtom_id][2])

        if osm_speed is not None and tomtom_speed is not None:
            osm_speed = float(osm_speed)

            plt.plot(osm_speed, tomtom_speed, 'kx', alpha = 0.5)

            if not osm_speed in aggregated:
                aggregated[osm_speed] = []

            aggregated[osm_speed].append(tomtom_speed)
            n += 1

    aggregates = { k : np.median(aggregated[k]) for k in aggregated }

    sorted_keys = sorted(aggregates.keys())
    sorted_values = [aggregates[k] for k in sorted_keys]

    x = np.linspace(0, 120)
    plt.plot(x, x, 'b--')

    #plt.plot(sorted_keys, sorted_values, 'rx-')
    plt.errorbar(sorted_keys, sorted_values, yerr = [np.std(aggregated[k]) for k in sorted_keys], color = 'r', marker = "x")
    plt.xlabel("Speed Limit [km/h]")
    plt.ylabel("Average TomTom Offpeak Speed [km/h]")
    plt.title("Manually matched links with speed info: %d" % n)
    plt.grid()

    #plt.show()
    plt.savefig("validated_links.png")
