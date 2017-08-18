#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Franz Papst
"""

import os
import random
import numpy as np
from glob import glob
from collections import OrderedDict

from bfcr import BFCR
from config import LABEL_DIR, TEST_SIZE, NUM_BASES, MGCORD, MGC_DIR, TRAINING_FILES, TEST_FILES

def split_training_test(prefix=None, test_size=TEST_SIZE):
    """Divides the files into training and test files.

    This helper function randomly divides the files into test and training
    data. It stores the name of the file into two text files, one for training
    and one for test data, named training_files.txt and test_files.txt. If a
    prefix is given the names of the files are appended to it, it is useful
    when trying different methods. The default value of test_files is stored in
    config.py.

    :params prefix: a prefix for the text file where the used filenames are stored
    :params test_size: number of test files
    :returns: list of training files
    :returns: list of test files
    """
    if prefix is None:
        prefix = ''

    training_files = [os.path.basename(os.path.splitext(i)[0]) for i in glob(LABEL_DIR + '*.lab')]
    test_files = []

    while len(test_files) < test_size:
        test_file = int(random.uniform(0, len(training_files)))
        test_files.append(training_files.pop(test_file))
    test_files = sorted(test_files)
    training_files = sorted(training_files)

    with open(prefix + TRAINING_FILES, 'w') as f:
        for i in training_files:
            f.write(i + '\n')

    with open(prefix + TEST_FILES, 'w') as f:
        for i in test_files:
            f.write(i + '\n')

    return training_files, test_files


def create_bfcr(filename):
    """Creates a BFCR instance for a given file.

    This helper function loads a label file and its corrosponding mgc file and
    creates a bfcr file from them. The paths of both files are determined
    automatically.

    :params filename: filename from which the BFCR instaces are created
    :returns: an instance of the BFCR class
    """
    filename = os.path.splitext(os.path.basename(filename))[0]

    label_file = LABEL_DIR + filename + '.lab'
    mgc_file = MGC_DIR + filename + '.mgc'

    mgc_matrix = np.fromfile(mgc_file, dtype=np.float32).reshape(-1, MGCORD+1)
    bfcr = BFCR(label_file)
    bfcr.encode_feature(mgc_matrix, 'mgc', NUM_BASES)
    return bfcr


def phone_to_num(phone_values):
    """Converts all phone strings into numerical values.

    This helper function iterates over a set of different phones and returns an
    alphabetically orderd directory where the phone string is the key and the
    numerical value is the corrosponding value.

    :params phone_values: a set (or list) of phone values
    :returns: an ordered directory with the numerical values as values
    """
    phone_values = OrderedDict.fromkeys(sorted(phone_values))
    for i,k in enumerate(phone_values.keys()):
        phone_values[k] = i
    phone_values['None'] = -1
    return phone_values
