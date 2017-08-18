#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Franz Papst
"""

import os
import pickle
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

from resynthesize import resynthesize
from config import MGCORD, NUM_BASES, LF0_DIR, TEST_FILES, REGRESSION_SAVED, OUT_DIR
from prediction import Prediction
from utils import split_training_test, create_bfcr, phone_to_num

class Regression:

    """Dummy class for saving regression related values.

    This class is used to easily store the filenames of the trained regression
    models and the integer values of the phones into a binary file.

    """

    def __init__(self, models, phone_values):
        """Initialises the instance with the filenames of the trained
        regression models and the directory of the numerical phone values.
        """
        self._models = models
        self._phone_values = phone_values

    @property
    def models(self):
        """Getter for the filenames of the trained models.

        :returns: filenames of the trained models
        """
        return self._models

    @property
    def phone_values(self):
        """Getter for the direcotry contaning the numerical values of phones.

        :returns: directory with numerical phone values
        """
        return self._phone_values


def train_regression(training_files, models={'Linear Regression':LinearRegression(n_jobs=8), 'Random Forest Regressor 10': RandomForestRegressor(10), 'Random Forest Regressor 50': RandomForestRegressor(50)}):
    """Trains a regression model.

    This function trains a regression model for the given training files.
    Before the training it creates a BFCR instace for all training files and
    collects all the different phones in the test data. Once the training
    is done it saves them as a binary file. Instead of returning a trained
    model, it retuns the filename of the saved trained models. This is done
    because especially the random forest regressor takes a lot of memory and
    having multiple instance of it can easily fill up all available memory,
    thus they are "swapped out".
    By default the used models are linear regression, a random forest regressor
    with 10 trees and a random forest regressor with 50 trees.

    :params training_files: a list of training files for the models
    :params models: a directory with the name and instance of the used model
    :returns: an instance of the dummy class Regression
    """
    phone_values = set()
    BFCR_training = []
    for i in training_files:
        bfcr = create_bfcr(i)
        BFCR_training.append(bfcr)

        for j in bfcr.label.cur_phones():
            phone_values.add(j)

    phone_values = phone_to_num(phone_values)

    y = []
    X = []
    for i in BFCR_training:
        for j in i.label.phones:
            X.append([phone_values[str(l)] for l in j.quinphone])

        mgc_coefficients = i.phone_coefficients('mgc')
        for k in range(mgc_coefficients.shape[0]):
            y.append(mgc_coefficients[k,:])
    X = np.reshape(X, (len(X), len(X[0])))
    y = np.reshape(y, (len(y), (MGCORD+1)*NUM_BASES))

    for key,model in models.items():
        model.fit(X, y)
        model_filename = key.replace(' ', '_')
        with open('TRAINED_' + model_filename + '.pickle', 'wb') as f:
            pickle.dump(model, f)
        models[key] = model_filename
        print('Trained {:s}'.format(model_filename))

    regression = Regression(models, phone_values)

    with open(REGRESSION_SAVED, 'wb') as f:
        pickle.dump(regression, f)
    print('Saving done')

    return regression


def predict_regression(regression, test_files, output_dir=None, create_original=True):
    """Predicts for the given test files from given regression models.

    This function creates a new *.wav file from the predictions of the given
    test files for all given regression models as well as a *.wav file from the
    original matrix. Furthermore it  adds the predicted values to a list of the
    prediction class, which is used for creating plots.
    If a trained model that is given in the regression istance is not found
    this function prints an error message and continues.

    By default a *.wav file of the orginal is created and the default path is
    ./wavs/regression.

    :params regression: instance of Regressin dummy class
    :params test_files: a list of test files
    :params output_dir: directory where the *.wav files are created
    :params create_original: wether to create an *.wav of the orginal or not
    :returns: list of predictions with results from the regression mdoels
    """
    models = regression.models
    phone_values = regression.phone_values

    if output_dir is None:
        output_dir = 'wavs/regression/'

    BFCR_test = []
    for i in test_files:
        bfcr = create_bfcr(i)
        BFCR_test.append(bfcr)

        if create_original:
            original_mgc = bfcr.original_matrix('mgc')
            lf0_filename = LF0_DIR + i + '.lf0'
            resynthesize(original_mgc, lf0_filename, output_dir + '{0:s}_original.wav'.format(i))

    predictions = [Prediction(os.path.splitext(os.path.basename(bfcr.label_file))[0]) for bfcr in BFCR_test]

    for k,v in models.items():
        try:
            with open('TRAINED_' + v + '.pickle', 'rb') as f:
                loaded_model = pickle.load(f)
                print('Loaded: {:s}'.format(v))
        except FileNotFoundError:
            print('Could not open {:s}'.format('TRAINED_' + v + '.pickle'))

        for i, bfcr in enumerate(BFCR_test):
            X = []
            for j in bfcr.label.phones:
                X.append([phone_values[str(l)] for l in j.quinphone])

            X = np.reshape(X, (len(X), len(X[0])))
            y = loaded_model.predict(X)

            bfcr.encoded_features = {'mgc':np.reshape(y, (y.shape[0], MGCORD+1, NUM_BASES))}
            predicted_mgc = bfcr.decode_feature('mgc')

            xmax_predicted = predicted_mgc.shape[0]
            x_prediction = np.linspace(0, xmax_predicted, xmax_predicted)

            predictions[i].add(k, x_prediction, predicted_mgc)

            lf0_filename = LF0_DIR + test_files[i] + '.lf0'
            resynthesize(predicted_mgc, lf0_filename, output_dir + '{0:s}_reconstructed_{1:s}.wav'.format(test_files[i], k.replace(' ', '_')))

    print('Predicting and resynthesising done')
    return predictions


if __name__ == '__main__':
    # trains (if no trained models are found) and uses regression models to
    # create *.wav files and plots for different regression models it also
    # prints the MSE values for the different models
    PREFIX = 'regression_'
    if not os.path.exists(REGRESSION_SAVED):
        training_files, test_files = split_training_test(PREFIX)
        model = train_regression(training_files)
    else:
        with open(REGRESSION_SAVED, 'rb') as f:
            model = pickle.load(f)

    with open(PREFIX + TEST_FILES, 'r') as f:
        test_files = f.readlines()
        test_files = [t.strip() for t in test_files]

    predictions = predict_regression(model, test_files)

    for p in predictions:
        filename = p.filename + '.png'
        p.plot_all(OUT_DIR + '/regression/' + filename)
        p.calc_error()
    print('Plotting done')
