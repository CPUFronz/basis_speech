#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Franz Papst
"""

import os
import pickle
import numpy as np
from sklearn.mixture import GaussianMixture

from utils import split_training_test, create_bfcr, phone_to_num
from config import TEST_FILES, LF0_DIR, MGCORD, NUM_BASES, GMM_SAVED, OUT_DIR
from resynthesize import resynthesize
from prediction import Prediction

MIN_INSTANCES = 3

class hierachical_gaussian:

    """A gaussian mixture model with differernt layers.

    This class implements a gaussian mixture model with different layer. It
    holds three different layers for quin-, tri- and single-phones. Once
    trained, it will use to look up, if there is a GMM for a given quin-phone,
    if not it will look if there is a GMM for a given tri-phone, if not it will
    just use a single phone to sample the coefficients for a phone.

    """

    def __init__(self, X, y):
        """Initialises the instance with for a given X and y.

        Creates all needed member variables and populates the directories
        representing the different types of phones (qui, tri or single). While
        populating it also converts the strings into a numerical values.

        :param X: quin-phones for training the model
        :param y: coefficients for the given phones
        """
        self._phone_values = set()
        self._single_phones = {}
        self._tri_phones = {}
        self._quin_phones = {}
        self._single_predictor = {}
        self._tri_predictor = {}
        self._quin_predictor = {}

        for p in X:
            self._phone_values.add(p[2])
        self._phone_values = phone_to_num(self._phone_values)

        for i,p in enumerate(X):
            self._single_phones = self._add_to_dict(self._single_phones, p[2], y[i])
            self._tri_phones = self._add_to_dict(self._tri_phones, p[1:3], y[i])
            self._quin_phones = self._add_to_dict(self._quin_phones, p, y[i])

        # change the key to a numerical value and remove keys with too little instances
        self._single_phones = {self._phone_values[key]:value for key,value in self._single_phones.items()}
        self._tri_phones = {tuple([self._phone_values[str(k)] for k in key]):value for key,value in self._tri_phones.items() if len(value) > MIN_INSTANCES and value.ndim == 2}
        self._quin_phones = {tuple([self._phone_values[str(k)] for k in key]):value for key,value in self._quin_phones.items() if len(value) > MIN_INSTANCES and value.ndim == 2}

    def train(self):
        """Trains the tree different layers of the model.

        This method trains the GMMs for every quin-, tri- or single-phone that
        has been passed to the constructor
        """
        self._single_predictor = self._train_hierarchy(self._single_phones)
        self._tri_predictor = self._train_hierarchy(self._tri_phones)
        self._quin_predictor = self._train_hierarchy(self._quin_phones)

    def sample(self, X):
        """Samples from the GMMs for a given input.

        This method checks if there is a model for a given input from the most
        specific one to the most general one. First it checkes if there is a
        model for the whole quin-phone, if not it checks if there is a model
        for the tri-phones, if still no model is found it samples the single
        phone.

        :param X: quin-phone for sapmling
        :returns: the sampled phone coefficients
        """
        coefficients = []

        for x in X:
            quin = tuple([self._phone_values[str(p)] for p in x])
            tri = tuple([self._phone_values[str(p)] for p in x[1:3]])
            single = self._phone_values[str(x[2])]

            if quin in self._quin_predictor:
                coefficients.append(self._quin_predictor[quin].sample())
            elif tri in self._tri_predictor:
                coefficients.append(self._tri_predictor[tri].sample())
            else:
                coefficients.append(self._single_predictor[single].sample())

        coefficients = [i[0] for i in coefficients]
        coefficients = np.squeeze(np.array(coefficients))
        return coefficients

    def _train_hierarchy(self, hierarchy):
        """Trains a hierarchy (quin-, tri- or single-phones).

        This helper method fits a GMM for all phones of one hierarchy.

        :param hierarchy: all phones of one hierarchy
        :returns: fitted GMMs for the given hierarchy
        """
        output = dict.fromkeys(hierarchy.keys())

        for k in output.keys():
            gm = GaussianMixture()
            gm.fit(hierarchy[k])
            output[k] = gm
            print('Fitted {:s}'.format(''.join(str(k))))
        return output

    def _add_to_dict(self, directory, key, value):
        """Adds a row of coefficients for given phones to a given directory.

        This helper method creates a new numpy array in the given directory if
        the given phone is not existing or stacks a row of coefficients to that
        phone.

        :params directory: the directory to add the coefficients
        :params key: the phone to create or add in the directory
        :params value: the coefficients to add
        :returns: the given directory with the added new coefficients
        """
        if key in directory:
            tmp = directory[key]
            tmp = np.vstack((tmp, value))
            directory[key] = tmp
        else:
            directory[key] = np.array(value)
        return directory

def train_gmm(training_files):
    """Trains a hierachical gaussian model.

    This function trains a hierarchical gaussian model for the given training
    files. Before the training it creates a BFCR instace for all training files
    and collects all the different phones in the test data. Once the training
    is done it saves them as a binary file.

    :params training_files: a list of training files for the model
    :returns: a trained hierarchical gaussian model
    """
    BFCR_training = []
    X = []
    y = []

    phone_values = set()

    for training_file in training_files:
        bfcr = create_bfcr(training_file)
        BFCR_training.append(bfcr)

        coefficients = bfcr.phone_coefficients('mgc')

        for i, p in enumerate(bfcr.label.cur_phones()):
            phone_values.add(p)

            X.append(tuple(bfcr.label.phones[i].quinphone))
            y.append(coefficients[i,:])

    phone_values = phone_to_num(phone_values)

    hgm = hierachical_gaussian(X,y)
    hgm.train()

    with open(GMM_SAVED, 'wb') as f:
        pickle.dump(hgm, f)
        print('Saved trained GMM')

    return hgm


def predict_gmm(hgm, test_files, output_dir=None, create_original=True):
    """Creates predictions for the given test files for a given GMM.

    This function creates a new *.wav file from the predictions of the given
    test files as well as a *.wav file from the original matrix. Furthermore it
    adds the predicted values to a list of the prediction class, which is used
    for creating plots.
    By default a *.wav file of the orginal is created and the default path is
    ./wavs/gmm.

    :params hgm: the hierarchical gaussian model to use
    :params test_files: a list of test files
    :params output_dir: directory where the *.wav files are created
    :params create_original: wether to create an *.wav of the orginal or not
    :returns: list of predictions with results from the GMM
    """
    BFCR_test = []
    MODEL = 'GMM'

    if output_dir is None:
        output_dir = 'wavs/gmm/'

    for test_file in test_files:
        bfcr = create_bfcr(test_file)
        BFCR_test.append(bfcr)

        if create_original:
            original_mgc = bfcr.original_matrix('mgc')
            lf0_filename = LF0_DIR + test_file + '.lf0'
            resynthesize(original_mgc, lf0_filename, output_dir + '{0:s}_original.wav'.format(test_file))

    predictions = [Prediction(os.path.splitext(os.path.basename(bfcr.label_file))[0]) for bfcr in BFCR_test]

    for i,bfcr in enumerate(BFCR_test):
        X = []
        for j,_ in enumerate(bfcr.label.cur_phones()):
            X.append(bfcr.label.phones[j].quinphone)

        y = hgm.sample(X)

        bfcr.encoded_features = {'mgc':np.reshape(y, (y.shape[0], MGCORD+1, NUM_BASES))}
        predicted_mgc = bfcr.decode_feature('mgc')

        xmax_predicted = predicted_mgc.shape[0]
        x_prediction = np.linspace(0, xmax_predicted, xmax_predicted)

        predictions[i].add(MODEL, x_prediction, predicted_mgc)

        lf0_filename = LF0_DIR + test_files[i] + '.lf0'
        resynthesize(predicted_mgc, lf0_filename, output_dir + '{0:s}_reconstructed_{1:s}.wav'.format(test_files[i], MODEL))

    print('Predicting and resynthesising done')
    return predictions

if __name__ == '__main__':
    # trains (if no trained model is found) and uses the hierarchical gaussian
    # model for creating *.wav files and plots, also computes the mean of
    # the MSE values of 25 different runs
    PREFIX = 'gmm_'
    if not os.path.exists(GMM_SAVED):
        training_files, test_files = split_training_test(PREFIX)
        hgm = train_gmm(training_files)
    else:
        with open(GMM_SAVED, 'rb') as f:
            hgm = pickle.load(f)

    with open(PREFIX + TEST_FILES, 'r') as f:
        test_files = f.readlines()
        test_files = [t.strip() for t in test_files]

    RUNS = 25
    mmse = []

    for i in range(RUNS):
        print('##################################################')
        print('RUN: {:d}'.format(i))
        print('##################################################')

        predictions = predict_gmm(hgm, test_files, 'wavs/gmm_{0:d}_runs/run_{1:d}/'.format(RUNS,i))

        for p in predictions:
            filename = p.filename + '_RUN_' + str(i).zfill(2) + '_' + '.png'
            p.plot_all(OUT_DIR + '/gmm/' + filename)
            mmse.append(p.calc_error())

    models = predictions[0].get_models()
    mmse = np.array(mmse)
    avg_mse = []

    LOG_DIR = './logs/'
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    with open(LOG_DIR + 'average_mse.txt', 'w') as avg_file:
        np.set_printoptions(threshold=np.nan)
        for i in range(len(test_files)):
            errors = mmse[i::len(test_files)]

            with open(LOG_DIR + test_files[i]+'_mse.txt', 'w') as mse_log:
                mse_log.write(str(models).strip('[]') + '\n')
                mse_log.write(np.array2string(errors, max_line_width=120).replace('[', '').replace(']', '').replace('  ', ' '))

            avg = errors.mean(axis=0)
            avg_mse.append(avg)

            avg_file.write('-------------------------------------------\n')
            avg_file.write('File: {:s}\n'.format(test_files[i]))
            for idx, mse in enumerate(avg):
                avg_file.write('Average MSE for {0:s}: {1:f}\n'.format(models[idx], mse))

    print('Done')
