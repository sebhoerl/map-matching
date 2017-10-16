import numpy as np
import pickle
import matplotlib.pyplot as plt
from tqdm import tqdm

def analyze(matching, osm_data, tomtom_data, threshold, aggregator, aggregator_name):
    plt.figure()

    aggregated = {}
    n = 0

    for tomtom_id, osm_id in tqdm(matching.items()):
        osm_speed = osm_data[osm_id][3]
        tomtom_speed = tomtom_data[tomtom_id][3]

        osm_class = osm_data[osm_id][2]
        tomtom_class = tomtom_data[tomtom_id][2]

        if osm_speed is not None and tomtom_speed is not None:
            osm_speed = float(osm_speed)

            plt.plot(osm_speed, tomtom_speed, 'kx', alpha = 0.5)

            if not osm_speed in aggregated:
                aggregated[osm_speed] = []

            aggregated[osm_speed].append(tomtom_speed)
            n += 1

    aggregates = { k : aggregator(aggregated[k]) for k in aggregated }

    sorted_keys = sorted(aggregates.keys())
    sorted_values = [aggregates[k] for k in sorted_keys]

    x = np.linspace(0, 120)
    plt.plot(x, x, 'b--')

    plt.errorbar(sorted_keys, sorted_values, yerr = [np.std(aggregated[k]) for k in sorted_keys], color = 'r', marker = "x")
    plt.xlabel("Speed Limit [km/h]")
    plt.ylabel("Average TomTom Offpeak Speed [km/h]")
    plt.title("Manually matched links with speed info: %d" % n)
    plt.grid()

    plt.savefig("output/speeds_%s_%d.png" % (aggregator_name, threshold))

    with open("output/speeds_%s_%d.p" % (aggregator_name, threshold), "wb+") as f:
        pickle.dump(aggregates, f)

    plt.close()

if __name__ == "__main__":
    osm_data = pickle.load(open("data/osm.p", "rb"))
    tomtom_data = pickle.load(open("data/tomtom.p", "rb"))

    for threshold in (10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
        matching = pickle.load(open("data/matching_%d.p" % threshold, "rb"))
        analyze(matching, osm_data, tomtom_data, threshold, np.mean, "mean")
        analyze(matching, osm_data, tomtom_data, threshold, np.median, "median")
