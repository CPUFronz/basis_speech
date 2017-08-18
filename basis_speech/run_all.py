#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Franz Papst
"""
import os
import pickle

from utils import split_training_test
from config import REGRESSION_SAVED, GMM_SAVED, TEST_FILES
from regression import train_regression, predict_regression
from gm_fitting import train_gmm, predict_gmm

if __name__ == '__main__':
    #trains all models and creates predictions for them
    if not os.path.exists(REGRESSION_SAVED) or not os.path.exists(GMM_SAVED):
        training_files, test_files = split_training_test()

        regression = train_regression(training_files)
        hgm = train_gmm(training_files)
    else:
        with open(GMM_SAVED, 'rb') as f:
            hgm = pickle.load(f)
        with open(REGRESSION_SAVED, 'rb') as f:
            regression = pickle.load(f)

    with open(TEST_FILES, 'r') as f:
        test_files = f.readlines()
        test_files = [t.strip() for t in test_files]

    predictions = predict_regression(regression, test_files, 'wavs/all/')
    predictions_gmm = predict_gmm(hgm, test_files, 'wavs/all/', False)

    for i,p in enumerate(predictions):
        for k,X,y in predictions_gmm[i].get_all():
            p.add(k,X,y)

    for p in predictions:
        p.plot_all()
        p.calc_error()
    print('Plotting done')
