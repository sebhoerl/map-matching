import numpy as np
import pickle
import matplotlib.pyplot as plt
from tqdm import tqdm
from matplotlib import cm
import numpy.linalg as la

prior = 1
relevant_types = ("motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "service")

with open("data/osm.p", "rb") as f:
    osm_data = pickle.load(f)

with open("data/tomtom.p", "rb") as f:
    tomtom_data = pickle.load(f)

with open("data/sanitized_validation_matching.p", "rb") as f:
    sanitized_matching = pickle.load(f)

observations = np.zeros((len(relevant_types), 8))

for tomtom_id, osm_id in sanitized_matching.items():
    osm_class = osm_data[osm_id][2]
    tomtom_class = tomtom_data[tomtom_id][2]

    observations[osm_class, int(tomtom_class)] += 1

observations += prior

osm_given_tomtom = observations.T
for i in range(len(osm_given_tomtom)): osm_given_tomtom[i] /= np.sum(osm_given_tomtom[i])

with open("data/classes.p", "wb+") as f:
    pickle.dump(osm_given_tomtom, f)

plt.figure()

i = 0
for k, c in enumerate(relevant_types):
    #if not "_link" in c: and not "unclassified" == c:
    plt.bar(np.arange(8) + (i / 10) - 0.4, osm_given_tomtom.T[k], 1 / 10, label = c, color = cm.jet(i/8))
    i += 1

plt.grid()
plt.legend(title = "OSM Class", loc = "upper center")
plt.xlabel("TomTom Functional Road Class")
plt.ylabel("Model Probability")
plt.xlim([-0.4, 8 - 0.4])
plt.title("P(OSM | TomTom)")
plt.show()
