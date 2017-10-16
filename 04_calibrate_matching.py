map_matching = __import__("05_map_matching")
import pickle
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    alpha, beta, gamma, threshold = 0.027, 1, -2.6, 1

    with open("data/sanitized_validation_matching.p", "rb") as f:
        sanitized_matching = pickle.load(f)

    original_osm_data = pickle.load(open("data/osm.p", "rb"))
    original_tomtom_data = pickle.load(open("data/tomtom.p", "rb"))
    class_probs = pickle.load(open("data/classes.p", "rb"))

    tomtom_data = { tomtom_id : tomtom_row for tomtom_id, tomtom_row in original_tomtom_data.items() if tomtom_id in sanitized_matching }

    osm_data = original_osm_data
    #osm_data = { osm_id : osm_row for osm_id, osm_row in original_osm_data.items() if osm_id in sanitized_matching.values() }

    alphas = []
    rates = []

    for threshold in np.linspace(0.0, 1.0, 10):
        matching = map_matching.perform_matching(osm_data, tomtom_data, class_probs, alpha, beta, gamma, threshold * 100)

        total = 0
        correct = 0

        unmatched = 0

        for tomtom_id, osm_id in sanitized_matching.items():
            total += 1

            if tomtom_id in matching and osm_id == matching[tomtom_id]:
                correct += 1

        alphas.append(threshold)
        rates.append((correct / total) / threshold)

    plt.figure()
    plt.plot(alphas, rates, 'b')
    plt.show()
