import json
import os.path
import sys
from os import path

import matplotlib.pyplot as plt
import numpy as np
from imageio import imread
from matplotlib import gridspec

with open(sys.argv[1]) as f:
    data = json.load(f)
picture_indices = [i for datapoint in data for i in (
    datapoint["left"], datapoint["right"])]
picture_paths = [
    f"pics/ILSVRC2012_test_{i:08d}.zoom00.JPEG" for i in picture_indices]
pics = [imread(path) for path in picture_paths]

labels = []
for datapoint in data:
    cur_labels = [1, 0] if datapoint["label"] == 0 else [0, 1]
    labels.extend(cur_labels)

ncols = 10
nrows = 10
gs = gridspec.GridSpec(nrows, ncols, hspace=.25)

fig = plt.figure(figsize=(16, 16))
for i in range(ncols):
    for j in range(nrows):
        cur_index = i * ncols + j
        ax = fig.add_subplot(gs[i, j])
        ax.set_title("label: " + str(labels[cur_index]), fontdict={"fontsize": 8}, pad=4)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        plt.imshow(pics[cur_index])
plt.savefig("fig.png", bbox_inches="tight")
