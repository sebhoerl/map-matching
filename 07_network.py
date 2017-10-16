import numpy as np
import pickle
import matplotlib.pyplot as plt
from tqdm import tqdm
import gzip
import re

with gzip.open("output/mmNetwork.xml.gz", "w+") as fout:
    with gzip.open("input/mmNetwork.xml.gz", "r") as fin:
        for line in tqdm(fin):
            if b"freespeed" in line:
                speed = float(re.search(b'freespeed="(.*?)"', line).group(1)) * 3600 / 1000

                if speed < 45:
                    speed -= 5
                elif speed < 55:
                    speed -= 20
                else:
                    speed -= 10

                speed = speed * 1000 / 3600

                line = re.sub(b'freespeed="(.*?)"', b'freespeed="%f"' % speed, line)
            fout.write(line)
