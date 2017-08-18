#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Franz Papst
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from collections import Counter

from label import Label
from config import MGCORD, SAMPFREQ, FRAMESHIFT, NR_OCCURENCES
from config import OUT_DIR, DATA_DIR

NUM_COMPONENTS = 3

def mark_phone(mgc, txt, labelpart, start, end, out_filename):
    """Plots the first three rows of the mgc and highlights a stated area.

    This function creates a plot of the first three rows of the mgc matrix and
    marks the area where that phone occurs with vertical bars.

    :params mgc: the mgc matrix to plot (the first three rows of it)
    :params txt: the sentence represented by the mgc
    :params labelpart: the part of the lable representing the phone and its
                    preedecessor and followers
    :params start: starting time of the phone to mark
    :params end: ending time of the phone to mark
    :params out_filename: the filename where the plot is saved
    """
    time_x = np.arange(mgc.shape[0]) * (FRAMESHIFT/SAMPFREQ)

    f,ax = plt.subplots(1, 1, figsize=(12,4))
    for i in range(NUM_COMPONENTS):
        ax.plot(time_x, mgc[:,i])

    ax.axvline(start, color='black')
    ax.axvline(end, color='black')
    ax.set_title(txt + '\n' + labelpart)
    f.tight_layout()
    f.savefig(out_filename)
    plt.close()


def plot_phones(data_dir, max_occurrences=10):
    """Creates plots for all phones found in label files.

    This function creates a plot for every phone it finds in a label file in
    the given data directory. By default it only creates ten plots per phone.

    :params data_dir: the directory to search for label, mgc and text files
    :params max_occurrences: number of plots to make per single phone
    """
    mgc_dir = data_dir + '/mgc/'
    txt_dir = data_dir + '/txt/'
    label_dir = data_dir + '/labels/full/'

    filenames = list(map(lambda x: x.replace(mgc_dir, '').replace('mgc', ''), glob(mgc_dir + '*')))
    filenames.sort()
    phones = Counter()
    for f in filenames:
        with open(txt_dir+f+'txt', 'r') as txt_line:
            label = Label(label_dir+f+'lab')
            mgc = np.fromfile(mgc_dir+f+'mgc', dtype=np.float32).reshape(-1, MGCORD+1)
            txt = txt_line.readline()

            for p in label.cur_phones_additions():
                if phones[p[0]] >= NR_OCCURENCES:
                    continue
                phones[p[0]] += 1

                if not os.path.exists(OUT_DIR + p[0]):
                    if not os.path.exists(OUT_DIR):
                        os.mkdir(OUT_DIR)
                    os.mkdir(OUT_DIR + p[0])

                out_filename = OUT_DIR + p[0] + '/' + p[0] + '_{:03d}.png'.format(phones[p[0]])
                mark_phone(mgc, txt, p[3].split('@')[0].split(' ')[-1], p[1], p[2], out_filename)
                print('Plot saved as {:s}'.format(out_filename))


if __name__ == '__main__':
    plot_phones(DATA_DIR)