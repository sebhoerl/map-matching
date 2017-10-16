import numpy as np
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt

def perform_matching(osm_data, tomtom_data, class_probs, alpha, beta, gamma, threshold):
    matching = {}

    osm_ids, osm_centroids, osm_angles, osm_highways = [], [], [], []
    tomtom_ids, tomtom_centroids, tomtom_angles, tomtom_highways = [], [], [], []
    osm_highways = []

    for link_id, (from_coord, to_coord, highway, maxspeed, nodes) in osm_data.items():
        difference = to_coord - from_coord

        osm_ids.append(link_id)
        osm_centroids.append(from_coord + 0.5 * difference)
        #osm_centroids.append(np.mean(nodes, axis = 0))
        osm_angles.append(np.arctan2(*difference[::-1]))
        osm_highways.append(highway)

    osm_centroids = np.array(osm_centroids, dtype = np.float)
    osm_angles = np.array(osm_angles, dtype = np.float)
    osm_highways = np.array(osm_highways, dtype = np.int)

    for link_id, (from_coord, to_coord, highway, speed, nodes) in tomtom_data.items():
        difference = to_coord - from_coord

        tomtom_ids.append(link_id)
        tomtom_centroids.append(from_coord + 0.5 * difference)
        #tomtom_centroids.append(np.mean(nodes, axis = 0))
        tomtom_angles.append(np.arctan2(*difference[::-1]))
        tomtom_highways.append(highway)

    tomtom_centroids = np.array(tomtom_centroids, dtype = np.float)
    tomtom_angles = np.array(tomtom_angles, dtype = np.float)
    tomtom_highways = np.array(tomtom_highways, dtype = np.int)

    tomtom_scores = {}

    tomtom_angles[tomtom_angles < 0.0] += 2 * np.pi
    osm_angles[osm_angles < 0.0] += 2 * np.pi
    tomtom_angles[tomtom_angles >= 2 * np.pi] -= 2 * np.pi
    osm_angles[osm_angles >= 2 * np.pi] -= 2 * np.pi

    matched_ids = set()

    for i in tqdm(range(len(tomtom_ids))):
        eucledian_distances = np.sqrt(np.sum((osm_centroids - tomtom_centroids[i])**2, axis = 1))

        angular_distances = np.abs(osm_angles - tomtom_angles[i])
        while np.any(angular_distances > 2 * np.pi) > 0:
            angular_distances[angular_distances > 2 * np.pi] -= 2 * np.pi
        angular_distances[angular_distances > np.pi] = 2 * np.pi - angular_distances[angular_distances > np.pi]

        distribution = class_probs[tomtom_highways[i]]
        probs = distribution[osm_highways]

        scores = alpha * eucledian_distances + beta * angular_distances + probs * gamma
        index = np.argmin(scores)

        if not np.isinf(scores[index]):
            matching[tomtom_ids[i]] = osm_ids[index]
            tomtom_scores[tomtom_ids[i]] = scores[index]
            matched_ids.add(tomtom_ids[i])

    quantile_score = np.percentile(list(tomtom_scores.values()), threshold)

    filtered_matching = {}

    for tomtom_id in matched_ids:
        if tomtom_scores[tomtom_id] <= quantile_score:
            filtered_matching[tomtom_id] = matching[tomtom_id]

    return filtered_matching

if __name__ == "__main__":
    osm_data = pickle.load(open("data/osm.p", "rb"))
    tomtom_data = pickle.load(open("data/tomtom.p", "rb"))
    class_probs = pickle.load(open("data/classes.p", "rb"))

    for threshold in (10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
        alpha, beta, gamma = 0.027, 1, -2.6

        matching = perform_matching(osm_data, tomtom_data, class_probs, alpha, beta, gamma, threshold)

        with open("data/matching_%d.p" % threshold, "wb+") as f:
            pickle.dump(matching, f)
