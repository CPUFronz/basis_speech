#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Franz Papst
"""

from phone import Phone

class Label:

    """A class representing the labels of the HTS-demo_CMU-ARCTIC-SLT dataset

    This class loads a label fire and parses it. Furthermore it provides easy
    access to phone related information like the start or end time of a phone.

    """

    def __init__(self, filename):
        """Initialises the instance with a given lable file.

        This method loads the given label file and populates the list of phones,
        which are parsed using the Phone class.

        :params filename: label file to be loaded
        """
        self.phones = []
        with open(filename, 'r') as f:
            for idx,l in enumerate(f.readlines()):
                self.phones.append(Phone(l,idx))

    def cur_phones(self):
        """This method iterates over all current phones.

        The current phone is the phone used for predicitions or plotting. In the
        label file it is given with additional information (like preceeding or
        following phones). This method iterates over the whole list of phones
        and always returns the current one

        :returns: the current phone
        """
        for l in self.phones:
            yield l.p3

    def cur_phones_additions(self):
        """Iterates over all phones and returns the current phone with additional information

        Like the method above, except that it also returns the beginning time, the
        end time and the line from the label file for that phone.

        :returns: the current phone
        :returns: beginning of the current phone
        :returns: end of the current phone
        :returns: whole line from the label file
        """
        for l in self.phones:
            yield l.p3, l.begin, l.end, l.original_line

    @property
    def first_phone_start(self):
        """Getter for the beginning time of the first phone.

        :returns: the beginning time of the first phone
        """
        return self.phones[0].begin

    @property
    def last_phone_end(self):
        """Getter for the end time of the last phone.

        :returns: the end time of the last phone
        """
        return self.phones[-1].end

    @property
    def num_phones(self):
        """Getter for the number of phones.

        :returns: the number of phones in the loaded label file
        """
        return len(self.phones)