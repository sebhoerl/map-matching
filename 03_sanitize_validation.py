import numpy as np
import shapefile
import pickle
import matplotlib.pyplot as plt
from tqdm import tqdm

with open("data/osm.p", "rb") as f:
    osm_data = pickle.load(f)

with open("data/tomtom.p", "rb") as f:
    tomtom_data = pickle.load(f)

vdata = [line.strip().split(';') for line in open("input/OSM2TomTom.csv")][1:]

plt.figure()

sanitized_matching = {}

for d in tqdm(vdata):
    if d[9] == "living_street" or d[9] == "track": continue

    tomtom_id, osm_id = d[1], d[6]

    tomtom_candidates = []
    if tomtom_id in tomtom_data: tomtom_candidates.append(tomtom_id)
    if "-" + tomtom_id in tomtom_data: tomtom_candidates.append("-" + tomtom_id)

    osm_candidates = []
    if osm_id in osm_data: osm_candidates.append(osm_id)
    if "-" + osm_id in osm_data: osm_candidates.append("-" + osm_id)

    tomtom_candidate_angles = np.unwrap([np.arctan2(*((np.array(tomtom_data[c][2:4]) - np.array(tomtom_data[c][0:2]))[::-1])) for c in tomtom_candidates])
    osm_candidate_angles = np.unwrap([np.arctan2(*((np.array(osm_data[c][2:4]) - np.array(osm_data[c][0:2]))[::-1])) for c in osm_candidates])

    tomtom_candidate_angles[tomtom_candidate_angles < 0.0] += 2 * np.pi
    osm_candidate_angles[osm_candidate_angles < 0.0] += 2 * np.pi
    tomtom_candidate_angles[tomtom_candidate_angles >= 2 * np.pi] -= 2 * np.pi
    osm_candidate_angles[osm_candidate_angles >= 2 * np.pi] -= 2 * np.pi

    indices = []
    distances = []

    for i in range(len(tomtom_candidate_angles)):
        for j in range(len(osm_candidate_angles)):
            pair = (tomtom_candidate_angles[i], osm_candidate_angles[j])
            diff = np.max(pair) - np.min(pair)
            if diff > np.pi: diff = 2 * np.pi - diff

            indices.append((i,j))
            distances.append(diff)

    distances = np.array(distances)
    distances[distances > np.pi] -= np.pi

    min_index = np.argmin(distances)

    i, j = indices[min_index]
    sanitized_matching[tomtom_candidates[i]] = osm_candidates[j]

with open('data/sanitized_validation_matching.p', 'wb+') as f:
    pickle.dump(sanitized_matching, f)
