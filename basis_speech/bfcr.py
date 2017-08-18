#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Franz Papst
"""

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

from label import Label
from config import MGCORD, NUM_BASES, DATA_DIR, SAMPFREQ, FRAMESHIFT, MGC_DIR, LABEL_DIR
from resynthesize import resynthesize

class BFCR:

    """ This class is a basis function representation of a given feature.

    It can decompose a given feature into a coefficients for basis functions,
    it uses Legendre polynomes to do so.
    Additional functionality is e.g. plotting a given component or blending
    between phone-borders of a recomposed matrix.

    """

    def __init__(self, label_file=None):
        """Initialises an instance.

        Note that a lable file doesn't necessarily have to be given at creation
        of an instance, it can also be set later with the method load_label()

        :params label_file: the label on which the BFCR instance is based
        """
        self._encoded_features = {}
        self._len_phones = {}
        self._original_matrix = {}
        if label_file:
            self.label = Label(label_file)
            self.label_file = label_file
        else:
            self.label = None
            self.label_file = None

    def load_label(self, filename):
        """Loads a label if not already loaded.

        :params filename: filename of the label
        :raises Exception: if a label is already loaded
        """
        if self.label is None:
            self.label = Label(filename)
            self.label_file = filename
        else:
            raise Exception('Label is already loaded')

    def encode_feature(self, feature_matrix, feature_name, num_bases=NUM_BASES):
        """Encodes a given feature.

        This method decomposes a given matrix into a matrix of cofficents of
        lengrande basis functions. The default value of basis functions to
        encode the matrix is given in config.py.

        :params feature_matrix: matrix to encode
        :params feature_name: name of the encoded feature
        :params num_bases: number of basis functions to encode
        :raises Exception: if no label is loaded
        """
        if self.label is None:
            raise Exception('No label file was loaded')

        num_components = feature_matrix.shape[1]
        step_size = feature_matrix.shape[0]/self.label.last_phone_end
        tensor = np.empty((self.label.num_phones, num_components, num_bases), dtype=np.float32)
        self._len_phones[feature_name] = []
        self._original_matrix[feature_name] = feature_matrix

        for i,phone in enumerate(self.label.cur_phones_additions()):
            phone_begin_index = int(round(phone[1]*step_size))
            phone_end_index = int(round(phone[2]*step_size))

            self._len_phones[feature_name].append((phone_begin_index,phone_end_index))

            for component in range(num_components):
                signal_snippet = feature_matrix[phone_begin_index:phone_end_index,component]
                x_values = np.linspace(-1, 1, len(signal_snippet))
                coeff = np.polynomial.legendre.legfit(x_values, signal_snippet, num_bases-1)
                tensor[i, component, :] = coeff

        self._encoded_features[feature_name] = tensor

    def decode_feature(self, feature_name, blending_time=None):
        """ Decodes a given feature.
        This method recomposes the matrix of basis function coefficients into a
        regular feature matrix. If blending_time is set the returned matrix
        will over the phone boarder for a given amount of milliseconds in both
        directions. By default no blending time is used.

        :params feature_name: name of the feature to decode
        :params blending_time: time to blend over the phone borders
        :returns: the recomposed matrix for the given feature
        """
        self._check_feature(feature_name)

        utterance_length = max(max(self._len_phones[feature_name]))
        reconstructed_matrix = np.zeros((utterance_length, self._encoded_features[feature_name].shape[1]), dtype=np.float32)

        for phone in range(len(self._len_phones[feature_name])):
            cur_phone_start = self._len_phones[feature_name][phone][0]
            cur_phone_end = self._len_phones[feature_name][phone][1]
            resample_size = len(range(cur_phone_start, cur_phone_end))
            x_values = np.linspace(-1, 1, resample_size)
            coeff = self._encoded_features[feature_name][phone][:][:]
            signal_snippet = np.zeros((len(x_values), coeff.shape[0]), dtype=np.float32)

            for i in range(coeff.shape[0]):
                signal_snippet[:,i] = np.polynomial.legendre.legval(x_values, coeff[i,:])

            reconstructed_matrix[cur_phone_start:cur_phone_end] = signal_snippet

        if blending_time:
            reconstructed_matrix = self._blend_borders(feature_name, reconstructed_matrix, blending_time)

        return reconstructed_matrix

    def save_to_file(self, filename):
        """Saves the bfcr instance into a binary file

        :params filename: name of the file where to save the BFCR instance
        """
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    def read_from_file(self, filename):
        """Loads a previous saved bfcr instance

        :params filename: name of the file to load the bfcr instance
        """
        with open(filename, 'rb') as f:
            restored = pickle.load(f)
            self.label = restored.label
            self._encoded_features = restored._encoded_features
            self._len_phones = restored._len_phones
            self._original_matrix = restored._original_matrix
            self.label_file = restored.label_file

    def plot_component(self, feature_name, filename, component_num=0):
        """Plots a component of a given feature

        This method creates a plot of a given feature and the original matrix
        of this feature. By default it plots only the first component of the
        matix.

        :params feature_name: name of the feature to plot
        :params filename: name of the file where the plot gets saved
        :params component_num: number of the component to plot
        """
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)

        xmax = self._original_matrix[feature_name].shape[0]
        f, ax = plt.subplots(1, 1, figsize=(18,6))
        x = np.linspace(0, xmax, xmax)
        ax.plot(x, self._original_matrix[feature_name][:,component_num], label='Original')
        ax.plot(x, self.decode_feature(feature_name)[:,component_num], '.', label='Reconstructed')
        ax.set_xlim(xmin=0, xmax=xmax)
        ax.legend()
        f.savefig(filename)
        plt.close()

    def original_matrix(self, feature_name):
        """Getter for the original matrix.

        :params feature_name: the feature of which to get the original matrix
        :returns: the original matrix of the given feature
        """
        return self._original_matrix[feature_name]

    def phone_coefficients(self, feature_name):
        """Get for basis function coefficients for all the phones. """
        self._check_feature(feature_name)
        num_phones = self._encoded_features[feature_name].shape[0]
        return np.reshape(self._encoded_features[feature_name], (num_phones, (MGCORD+1) * NUM_BASES))

    @property
    def encoded_features(self):
        """Get all encoded features."""
        return self._encoded_features

    @encoded_features.setter
    def encoded_features(self, value):
        """Set for encoded features."""
        if not self.label:
            raise Exception('No label file was loaded, labels are needed for assigning phone lenght')

        if type(value) is not dict:
            raise TypeError('encoded_features has to be assigned to a dict')

        for i in value.keys():
            self._encoded_features[i] = value[i]
            step_size = SAMPFREQ / FRAMESHIFT
            self._len_phones[i] = []
            for phone in self.label.cur_phones_additions():
                phone_begin_index = int(round(phone[1]*step_size))
                phone_end_index = int(round(phone[2]*step_size))

                self._len_phones[i].append((phone_begin_index,phone_end_index))

    def _blend_borders(self, feature_name, matrix, blending_time=25):
        """Blends over the borders of one phone to the next.

        This helper method blend from the end of one phone to the beginning of
        the following one. The default value of 25ms was found to give the best
        results.

        :params feature_name: name of the feature matrix to do the blending
        :params matrix: matrix to blend
        :params blending_time: time to blend over each border in milliseconds
        :returns: the given matrix with blended phone borders
        """
        blending_time = 1/1000*blending_time
        phone_borders = [phone[2] for phone in self.label.cur_phones_additions()]

        last_time = phone_borders[-1]
        last_index = self._len_phones[feature_name][-1][1]
        step = last_time/last_index

        for i in range(len(phone_borders)):
            if i == 0 or i == len(phone_borders)-1:
                continue

            if phone_borders[i]-blending_time < phone_borders[i-1] or phone_borders[i]+blending_time > phone_borders[i+1]:
                continue

            start = phone_borders[i] - blending_time
            end = phone_borders[i] + blending_time

            blend_index_start = round(start/step)
            blend_index_end = round(end/step)-1

            blend_start_values = matrix[blend_index_start, :]
            blend_end_values= matrix[blend_index_end, :]
            blend_factors = np.linspace(1,0, blend_index_end-blend_index_start)

            for j in range(len(blend_factors)):
                blend_factor = blend_factors[j]
                matrix[blend_index_start+j, :] = blend_factor*blend_start_values[:] + (1-blend_factor)*blend_end_values[:]

        return matrix

    def _check_feature(self, feature_name):
        """Checks if a feature is encoded, raises an exeption if not.

        :raises Exception. if the requested feature is not encoded.
        """
        try:
            self._len_phones[feature_name]
            self._encoded_features[feature_name]
        except KeyError:
            raise Exception('Feature "{:s}" is not encoded'.format(feature_name))


def plot_different_basis_functions(filename, basis_functions, plot_filename):
    """Encodes and plots the results for four different basis functions

    This function creates subplots for different basis functions and the
    original matrix. It is used to show the influence of different numbers of
    basis functions on the recomposition of the original matrix. If the list of
    baisis functions contains more than four values they are ignored.

    :params filename: name of the input file
    :params list of different numbers of basis functions to plot
    :params plot_filename: name of the file where the plots are saved
    """
    if len(basis_functions) > 4:
        basis_functions = basis_functions[:4]
        print('Can only plot the reconstrucation of 4 different basis functions, exceeding functions will be ommited')

    filename = os.path.splitext(os.path.basename(filename))[0]
    label_file = LABEL_DIR + filename + '.lab'
    mgc_file = MGC_DIR + filename + '.mgc'
    matrix_to_encode = np.fromfile(mgc_file, dtype=np.float32).reshape(-1, MGCORD+1)
    bfcr = BFCR(label_file)

    f = plt.figure(figsize=(18,6))
    ax = []
    ax.append(plt.subplot2grid((2,2), (0,0)))
    ax.append(plt.subplot2grid((2,2), (0,1)))
    ax.append(plt.subplot2grid((2,2), (1,0)))
    ax.append(plt.subplot2grid((2,2), (1,1)))

    for k,j in enumerate(basis_functions):
        bfcr.encode_feature(matrix_to_encode, 'mgc', j)
        reconstructed_mgc = bfcr.decode_feature('mgc')

        xsamples = bfcr.original_matrix('mgc').shape[0]
        xmax = bfcr.label.phones[-1].end
        xvalues = np.linspace(0, xmax, xsamples)

        ax[k].plot(xvalues, bfcr.original_matrix('mgc')[:,0], label='Original')
        ax[k].plot(xvalues, reconstructed_mgc[:,0], '.', label='Reconstructed')
        ax[k].set_title('Original MGC and Reconstructed MGC using {:d} basis functions'.format(j))
        ax[k].set_xlabel('Time [s]')
        ax[k].set_ylabel('Amplitude')
        ax[k].set_xlim(xmin=0, xmax=xmax)
        ax[k].legend(loc='lower center')

    f.tight_layout()
    f.savefig(plot_filename)


if __name__ == '__main__':
    # creates the plots for 1 to 25 basis functions for the first 10 mgc files

    for i in range(1,10):
        in_file = 'a00{:02d}'.format(i)
        lab_filename = DATA_DIR + '/labels/full/cmu_us_arctic_slt_' + in_file + '.lab'
        mgc_filename = DATA_DIR + '/mgc/cmu_us_arctic_slt_' + in_file + '.mgc'
        lf0_filename = DATA_DIR + '/lf0/cmu_us_arctic_slt_' + in_file + '.lf0'
        bfcr = BFCR(lab_filename)
        mgc_matrix = np.fromfile(mgc_filename, dtype=np.float32).reshape(-1, MGCORD+1)

        out_dir = 'wavs/bfcr_reconstructed/{:s}/'.format(in_file)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        resynthesize(mgc_matrix, lf0_filename, '{0:s}/{1:s}_original.wav'.format(out_dir,in_file))

        for j in range(1,26):
            bfcr.encode_feature(mgc_matrix, 'mgc', j)
            bfcr.plot_component('mgc', 'phone_plots/bfcr_reconstructed/{0:s}/{0:s}_mgc_{1:02d}_basefunctions.png'.format(in_file,j), 0)
            reconstructed_mgc = bfcr.decode_feature('mgc')

            resynthesize(reconstructed_mgc, lf0_filename, '{0:s}/{1:s}_reconstructed_{2:02d}_basefunctions.wav'.format(out_dir,in_file,j))
