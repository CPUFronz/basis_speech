#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Franz Papst
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from label import Label
from config import MGC_DIR, LABEL_DIR, DATA_DIR, COMPONENTS_TO_PLOT, MGCORD, OUT_DIR

class Prediction:

    """Class to collect and compare predictions made by different models.

    This class acts as a hub for collecting the results of the predictions made
    by different models for the same file and to all put them into one plot
    including the original matrix. It also calculates the mean squared error
    for the different predictions.
    """

    def __init__(self, filename, model=None, X=None, y=None):
        """Initialises the instance for a given test file.

        This method creates all needed member variables and populates them with
        values if given.

        :params filename: the name of the test file
        :params model: name of model to add
        :params X: values on which the prediction is based for a given model
        :params y: predicted values for X for a given model
        """
        self._filename = filename

        if all([model, X, y]):
            self._X = {model : X}
            self._y = {model : y}
        else:
            self._X = {}
            self._y = {}

    def add(self, model, X, y):
        """Adds the predicted values for a new model.

        :params model: name of the model to add
        :params X: values on which the prediction is based for a given model
        :params y: predicted values for X for a given model
        """
        self._X[model] = X
        self._y[model] = y

    def get_all(self):
        """Iterates over all models and returns the name, X and y values.

        :returns: name of the model
        :returns: values on which the prediction is based for a given model
        :returns: predicted values for X for a given model
        """
        for k in self._X.keys():
            yield k, self._X[k], self._y[k]

    def plot_all(self, plot_abs_filename=None, num_components=COMPONENTS_TO_PLOT):
        """Creates a plot with the predicted values of all models and the original.

        This method creates a plot with the predictions made by all added
        models and the original matrix. By default it only plots the first
        component and saves the plot in <OUT_DIR>/predictions/' (<OUT_DIR> is
        set in config.py).

        :params num_components: the number of components to plot (number of subplots)
        :params plot_abs-filename: the filename for saving the plots
        """
        if not plot_abs_filename:
            plot_abs_filename = os.path.splitext(os.path.basename(self._filename))[0]
            plot_abs_filename = OUT_DIR + '/predictions/' + plot_abs_filename + '.png'

        path = os.path.dirname(plot_abs_filename)
        if not os.path.exists(path) and path != '':
            os.makedirs(path)

        with open(DATA_DIR + '/txt/{:s}.txt'.format(self._filename), 'r') as f:
            txt = f.readline()

        original_matrix, starts = self._load_original_matrix()
        xmax_original = original_matrix.shape[0]
        x_original = np.linspace(0, xmax_original, xmax_original)

        f, ax = plt.subplots(num_components, 1, figsize=(30,6))

        if num_components == 1:
          ax = [ax]

        for j in range(num_components):
            ax[j].plot(x_original, original_matrix[:,j], label='Original')

        for k in self._X.keys():
            for j in range(num_components):
                ax[j].plot(self._X[k], self._y[k][:,j], label=k)

                for idx,_ in enumerate(starts):
                    ax[j].axvline(starts[idx], color='black')

                ax[j].set_xlim(xmin=0, xmax=max(xmax_original, self._X[k].max()))

        ax[0].set_title(txt)
        ax[0].legend()

        f.savefig(plot_abs_filename)
        plt.close()

    def calc_error(self):
        """Calculates the mean squared error for all models.

        This method calculates and prints the mean squared error for all models
        in the Predication class.

        :returns: a list of all calculated MSEs
        """
        errors = []
        original_matrix, _ = self._load_original_matrix()

        print('-------------------------------------------')
        print('File: {:s}'.format(self._filename))
        for key,predicted_matrix in self._y.items():
            orig_x = original_matrix.shape[0]
            predicted_x = predicted_matrix.shape[0]
            x_max = min(orig_x, predicted_x)

            if orig_x > predicted_x:
                mse = ((original_matrix[0:x_max] - predicted_matrix)**2).mean()
            elif orig_x < predicted_x:
                mse = ((original_matrix - predicted_matrix[0:x_max])**2).mean()
            else:
                mse = ((original_matrix - predicted_matrix)**2).mean()

            print('MSE for {0:s}: {1:f}'.format(key, mse))
            errors.append(mse)
        return errors

    def get_models(self):
        """Retruns a list of all stored models.

        :returns: list of all stored models
        """
        models = []
        for i in self._y.keys():
            models.append(i)
        return models

    @property
    def filename(self):
        """Getter for name of the associated test file.
        :returns: the name of the test file
        """
        return os.path.splitext(self._filename)[0]

    def _load_original_matrix(self):
        """Loades the original mgc matrix for the test file.

        This helper method loads the original matrix from the *.mgc file and
        matrix for the test file and also computes the staring times of the
        different phones.

        :returns: the original mgc matrix
        :returns: starting times of the phones
        """
        mgc_matrix = np.fromfile(MGC_DIR + self._filename + '.mgc', dtype=np.float32).reshape(-1, MGCORD+1)

        label = Label(LABEL_DIR + self._filename + '.lab')
        step_size = mgc_matrix.shape[0]/label.last_phone_end
        phone_starts = [int(round(p[1]*step_size)) for p in label.cur_phones_additions()]

        return mgc_matrix, phone_starts
