import numpy as np
import shapefile
import pyproj
from tqdm import tqdm
import pickle

wgs84 = pyproj.Proj("+init=EPSG:4326")
lv03p = pyproj.Proj("+init=EPSG:2056")

def read_shapes(path):
    sf = shapefile.Reader(path)

    minx, maxx, miny, maxy = np.inf, -np.inf, np.inf, -np.inf

    geometry = {}

    for sr in tqdm(sf.shapeRecords(), desc = "Reading shapes ..."):
        points = np.array(sr.shape.points)

        x, y = pyproj.transform(wgs84, lv03p, points[:,0], points[:,1])
        x, y = np.array(x).reshape((len(x), 1)), np.array(y).reshape((len(y), 1))
        points = np.hstack((x, y))

        minx = min(minx, np.min(points[:,0]))
        maxx = max(maxx, np.max(points[:,0]))
        miny = min(miny, np.min(points[:,1]))
        maxy = max(maxy, np.max(points[:,1]))

        start_coord = points[0]
        end_coord = points[-1]

        if sr.record[2] == "FT" or sr.record[2] == b'  ':
            geometry[sr.record[0]] = (start_coord, end_coord, int(sr.record[1]), points)#, points)

        if sr.record[2] == "TF" or sr.record[2] == b'  ':
            geometry["-" + sr.record[0]] = (end_coord, start_coord, int(sr.record[1]), points)#, points)

    bounds = (minx, maxx, miny, maxy)

    return geometry

def read_speeds(prefix):
    month = 9
    day = 1

    speeds = {}
    counts = {}

    with tqdm(total = 3 * 30 + 1, desc = "Aggregating speeds ...") as progress:
        while not (month == 11 and day == 31):
            with open(prefix + "/Zurich-15_2015-%02d-%02d_speed.txt" % (month, day)) as f:
                for line in f:
                    parts = line.strip().split(",")

                    link = parts[0]
                    row = np.array(["NaN" if p == "" else p for p in parts[1:]], dtype=np.float)

                    mask = ~np.isnan(row)

                    if not link in speeds:
                        speeds[link] = np.zeros((96,), dtype=np.float)
                        counts[link] = np.zeros((96,), dtype=np.float)

                    speeds[link][mask] += row[mask]
                    counts[link][mask] += 1

            progress.update()
            day += 1

            if (month == 9 and day == 31) or (month == 10 and day == 32):
                day = 1
                month += 1

    average_speeds = {}

    for link_id in tqdm(speeds, desc = "Averaging speeds ..."):
        average_binned = speeds[link_id] / counts[link_id]
        average_offpeak = np.mean(average_binned[12 * 4:15 * 4])
        average_speeds[link_id] = average_offpeak if not np.isnan(average_offpeak) else None

    return average_speeds

def make_links(geometry, speeds):
    links = {}

    for link_id, link_geometry in tqdm(geometry.items(), "Merging spatial and speed data ..."):
        links[link_id] = (link_geometry[0], link_geometry[1], link_geometry[2], speeds[link_id] if link_id in speeds else None, link_geometry[3])#, link_geometry[2])

    return links

if __name__ == "__main__":
    geometry = read_shapes("input/shapes/zurich.shp")
    speeds = read_speeds("input/ZURICH")

    with open("data/tomtom.p", "wb+") as f:
        pickle.dump(make_links(geometry, speeds), f)
















#
