import numpy as np
import xml.sax
import pyproj
import pickle
from tqdm import tqdm

wgs84 = pyproj.Proj("+init=EPSG:4326")
lv03p = pyproj.Proj("+init=EPSG:2056")

relevant_types = ("motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "service", "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link")
relevant_main_types = ("motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "service")

class WayReader(xml.sax.ContentHandler):
    def __init__(self):
        self.reset_way()

        self.ways = {}
        self.nodes = set()

    def reset_way(self):
        self.way_id = None

        self.way_to = None
        self.way_from = None
        self.way_nodes = []

        self.way_highway = None
        self.way_maxspeed = None

        self.way_lanes = None
        self.way_lanes_forward = None
        self.way_lanes_backward = None

        self.way_oneway = None

    def startDocument(self):
        self.progress = tqdm(desc = "Loading ways ...")

    def startElement(self, name, attr):
        self.progress.update()

        if name == "way" and not ("visible" in attr and attr["visible"] == "false"):
            self.way_id = attr['id']
        elif self.way_id is not None:
            if name == "nd":
                self.way_to = attr['ref']
                self.way_nodes.append(self.way_to)
                if self.way_from is None: self.way_from = self.way_to
            elif name == "tag" and attr['k'] == "highway" and attr['v'] in relevant_types:
                self.way_highway = attr['v']
            elif name == "tag" and attr['k'] == "maxspeed":
                self.way_maxspeed = attr['v']
            elif name == "tag" and attr['k'] == "lanes":
                self.way_lanes = attr['v']
            elif name == "tag" and attr['k'] == "lanes:forward":
                self.way_lanes_forward = attr['v']
            elif name == "tag" and attr['k'] == "lanes:backward":
                self.way_lanes_backward = attr['v']
            elif name == "tag" and attr['k'] == "oneway":
                self.way_oneway = attr['v']

    def endElement(self, name):
        if name == "way":
            if not np.any([x is None for x in (self.way_id, self.way_to, self.way_from, self.way_highway)]):
                self.ways[self.way_id] = (self.way_to, self.way_from, self.way_highway, self.way_maxspeed, self.way_oneway, self.way_nodes)

                self.nodes.add(self.way_to)
                self.nodes.add(self.way_from)
                for node in self.way_nodes: self.nodes.add(node)

            self.reset_way()

class NodeReader(xml.sax.ContentHandler):
    def __init__(self, requested):
        self.requested = requested
        self.nodes = {}
        self.progress = None

    def startDocument(self):
        self.progress = tqdm(desc = "Loading nodes ...")

    def startElement(self, name, attr):
        self.progress.update()

        if name == "node" and attr['id'] in self.requested:
            x, y = pyproj.transform(wgs84, lv03p, float(attr['lon']), float(attr['lat']))
            self.nodes[attr['id']] = np.array((x,y))

def make_links(ways, nodes):
    progress = tqdm(total = len(ways), desc = "Generating links ...")
    links = {}

    for way_id, (to_id, from_id, highway, maxspeed, oneway, link_nodes) in ways.items():
        progress.update()

        points = np.array([nodes[n] for n in link_nodes])
        highway = relevant_main_types.index(highway.replace("_link", ""))

        if oneway is not None and (oneway == "yes" or oneway == "-1") or highway == "motorway":
            if oneway == "-1":
                links["-" + way_id] = (points[-1], points[0], highway, maxspeed, points)
            else:
                links[way_id] = (points[0], points[-1], highway, maxspeed, points)
        elif oneway is None or oneway == "no":
            links[way_id] = (points[0], points[-1], highway, maxspeed, points)
            links["-" + way_id] = (points[-1], points[0], highway, maxspeed, points)

    return links

if __name__ == "__main__":
    way_reader = WayReader()
    xml.sax.parse(open("input/zurich.osm"), way_reader)

    node_reader = NodeReader(way_reader.nodes)
    xml.sax.parse(open("input/zurich.osm"), node_reader)

    with open("data/osm.p", "wb+") as f:
        pickle.dump(make_links(way_reader.ways, node_reader.nodes), f)
