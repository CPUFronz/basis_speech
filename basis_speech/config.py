#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Franz Papst
"""

MGCORD = 34
SAMPFREQ = 48000.
FRAMESHIFT = 240.
FREQWARP = 0.55
GAMMA = 0
NR_OCCURENCES = 10
OUT_DIR = 'phone_plots/'
NUM_BASES = 5
DATA_DIR = '../tools/HTS-demo_CMU-ARCTIC-SLT/data/'
TEST_SIZE = 132
MGC_DIR = DATA_DIR + 'mgc/'
LABEL_DIR = DATA_DIR + 'labels/full/'
LF0_DIR = DATA_DIR + 'lf0/'
COMPONENTS_TO_PLOT = 1
TEST_FILES = 'test_files.txt'
TRAINING_FILES = 'training_files.txt'
GMM_SAVED = 'TRAINED_GMM.pickle'
REGRESSION_SAVED = 'TRAINED_REGRESSION.pickle'
