#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Franz Papst
"""

import re

class Phone:

    """A phone as defined in the HTS label format

    This class parses one line (=one phone) of the HTS label format.
    """

    def __init__(self, line, number_of_phone=None):
        """Initialises the instance with one line of the label file.

        :params line: the line to parse
        :params number_of_phones: number of the phone in the lable file
        """
        self.original_line = line
        if number_of_phone:
            self.number = number_of_phone
        else:
            self.number = None

        regex = re.compile(r'^ *(\d+) +(\d+)(.*)$')
        m = regex.match(line)

        if m:
            self.begin = int(m.group(1)) / 1e7
            self.end = int(m.group(2)) / 1e7
            rest = m.group(3).strip().split('/')
            self.__split_P(rest[0])
            self.__split_A(rest[1])
            self.__split_B(rest[2])
            self.__split_C(rest[3])
            self.__split_D(rest[4])
            self.__split_E(rest[5])
            self.__split_F(rest[6])
            self.__split_G(rest[7])
            self.__split_H(rest[8])
            self.__split_I(rest[9])
            self.__split_J(rest[10])

            self.p1_help = 'the phoneme identity before the previous phoneme'
            self.p2_help = 'the previous phoneme identity'
            self.p3_help = 'the current phoneme identity'
            self.p4_help = 'the next phoneme identity'
            self.p5_help = 'the phoneme after the next phoneme identity'
            self.p6_help = 'position of the current phoneme identity in the current syllable (forward)'
            self.p7_help = 'position of the current phoneme identity in the current syllable (backward)'
            self.a1_help = 'whether the previous syllable stressed or not'
            self.a2_help = 'whether the previous syllable accented or not'
            self.a3_help = 'the number of phonemes in the previous syllable'
            self.b1_help = 'whether the current syllable stressed or not'
            self.b2_help = 'whether the current syllable accented or not'
            self.b3_help = 'the number of phonemes in the current syllable'
            self.b4_help = 'position of the current syllable in the current word (forward)'
            self.b5_help = 'position of the current syllable in the current word (backward)'
            self.b6_help = 'position of the current syllable in the current phrase (forward)'
            self.b7_help = 'position of the current syllable in the current phrase (backward)'
            self.b8_help = 'the number of stressed syllables before the current syllable in the current phrase'
            self.b9_help = 'the number of stressed syllables after the current syllable in the current phrase'
            self.b10_help = 'the number of accented syllables before the current syllable in the current phrase'
            self.b11_help = 'the number of accented syllables after the current syllable in the current phrase'
            self.b12_help = 'the distance per syllable from the previous stressed syllable to the current syllable'
            self.b13_help = 'the distance per syllable from the current syllable to the next stressed syllable'
            self.b14_help = 'the distance per syllable from the previous accented syllable to the current syllable'
            self.b15_help = 'the distance per syllable from the current syllable to the next accented syllable'
            self.b16_help = 'name of the vowel of the current syllable'
            self.c1_help = 'whether the next syllable stressed or not'
            self.c2_help = 'whether the next syllable accented or not'
            self.c3_help = 'the number of phonemes in the next syllable'
            self.d1_help = 'gpos (guess part-of-speech) of the previous word'
            self.d2_help = 'the number of syllables in the previous word'
            self.e1_help = 'gpos (guess part-of-speech) of the current word'
            self.e2_help = 'the number of syllables in the current word'
            self.e3_help = 'position of the current word in the current phrase (forward)'
            self.e4_help = 'position of the current word in the current phrase (backward)'
            self.e5_help = 'the number of content words before the current word in the current phrase'
            self.e6_help = 'the number of content words after the current word in the current phrase'
            self.e7_help = 'the distance per word from the previous content word to the current word'
            self.e8_help = 'the distance per word from the current word to the next content word'
            self.f1_help = 'gpos (guess part-of-speech) of the next word'
            self.f2_help = 'the number of syllables in the next word'
            self.g1_help = 'the number of syllables in the previous phrase'
            self.g2_help = 'the number of words in the previous phrase'
            self.h1_help = 'the number of syllables in the current phrase'
            self.h2_help = 'the number of words in the current phrase'
            self.h3_help = 'position of the current phrase in this utterance (forward)'
            self.h4_help = 'position of the current phrase in this utterance (backward)'
            self.h5_help = 'TOBI endtone of the current phrase'
            self.i1_help = 'the number of syllables in the next phrase'
            self.i2_help = 'the number of words in the next phrase'
            self.j1_help = 'the number of syllables in this utterance'
            self.j2_help = 'the number of words in this utterance'
            self.j3_help = 'the number of phrases in this utterance'

    def __split_P(self, string):
        """Parses the current quin-phone.

        :params string: string to parse
        """
        rest = string.split('^')
        self._LL = self.__str2str(rest[0])
        rest = rest[1].split('-')
        self._L = self.__str2str(rest[0])
        rest = rest[1].split('+')
        self._C = self.__str2str(rest[0])
        rest = rest[1].split('=')
        self._R = self.__str2str(rest[0])
        rest = rest[1].split('@')
        self._RR = self.__str2str(rest[0])
        rest = rest[1].split('_')
        self._cur_phoneme_id_pos_forward = self.__str2int(rest[0])
        self._cur_phoneme_id_pos_backward = self.__str2int(rest[1])

    def __split_A(self, string):
        """Parses information about the previous syllable.

        :params string: string to parse
        """
        string = string[2:].split('_')
        self._prev_syll_stressed = self.__char2bool(string[0])
        self._prev_syll_accented = self.__char2bool(string[1])
        self._prev_syll_phoneme_num = self.__str2int(string[2])

    def __split_B(self, string):
        """Parses information about the current syllable.

        :params string: string to parse
        """
        string = string[2:].split('@')

        b1_3 = string[0].split('-')
        self._cur_syll_stressed = self.__char2bool(b1_3[0])
        self._cur_syll_accented = self.__char2bool(b1_3[1])
        self._cur_syll_phoneme_num = self.__str2int(b1_3[2])

        string = string[1].split('&')
        b4_5 = string[0].split('-')
        self._cur_syll_pos_current_word_forward = self.__str2int(b4_5[0])
        self._cur_syll_pos_current_word_backward = self.__str2int(b4_5[1])

        string = string[1].split('#')
        b6_7 = string[0].split('-')
        self._cur_syll_pos_cur_phrase_forward = self.__str2int(b6_7[0])
        self._cur_syll_pos_cur_phrase_backward = self.__str2int(b6_7[1])

        string = string[1].split('$')
        b8_9 = string[0].split('-')
        self._cur_syll_num_stressed_sylls_before_cur_phrase = self.__str2int(b8_9[0])
        self._cur_syll_num_stressed_sylls_after_cur_phrase = self.__str2int(b8_9[1])

        string = string[1].split('!')
        b10_11 = string[0].split('-')
        self._cur_syll_num_accented_sylls_before_cur_phrase = self.__str2int(b10_11[0])
        self._cur_syll_num_accented_sylls_after_cur_phrase = self.__str2int(b10_11[1])

        string = string[1].split(';')
        b12_13 = string[0].split('-')
        self._cur_syll_distance_prev_stressed_syll = self.__str2int(b12_13[0])
        self._cur_syll_distance_next_stressed_syll = self.__str2int(b12_13[1])

        string = string[1].split('|')
        b14_15 = string[0].split('-')
        self._cur_syll_distance_prev_accented_syll = self.__str2int(b14_15[0])
        self._cur_syll_distance_next_accented_syll = self.__str2int(b14_15[1])

        self._cur_syll_vowel = self.__str2str(string[1])

    def __split_C(self, string):
        """Parses information about the next syllable.

        :params string: string to parse
        """
        string = string[2:].split('+')
        self._next_syll_stressed = self.__char2bool(string[0])
        self._next_syll_accented = self.__char2bool(string[1])
        self._next_syll_num_phonems = self.__str2int(string[2])

    def __split_D(self, string):
        """Parses information about the guess part-of-speech of the previous word

        :params string: string to parse
        """
        string = string[2:].split('_')
        self._prev_word_gpos = self.__str2str(string[0])
        self._prev_word_num_syll = self.__str2int(string[1])

    def __split_E(self, string):
        """Parses information about the guess part-of-speech of the current word

        :params string: string to parse
        """
        string = string[2:].split('@')
        e1_2 = string[0].split('+')
        self._cur_word_gpos = self.__str2str(e1_2[0])
        self._cur_word_num_syll = self.__str2int(e1_2[1])

        string = string[1].split('&')
        e3_4 = string[0].split('+')
        self._cur_word_pos_cur_phrase_forward = self.__str2int(e3_4[0])
        self._cur_word_pos_cur_phrase_backward = self.__str2int(e3_4[1])

        string = string[1].split('#')
        e5_6 = string[0].split('+')
        self._cur_word_num_content_words_cur_phrase_before = self.__str2int(e5_6[0])
        self._cur_word_num_content_words_cur_phrase_after = self.__str2int(e5_6[1])

        e7_8 = string[1].split('+')
        self._cur_word_distance_prev_content_word = self.__str2int(e7_8[0])
        self._cur_word_distance_next_content_word = self.__str2int(e7_8[1])

    def __split_F(self, string):
        """Parses information about the guess part-of-speech of the next word

        :params string: string to parse
        """
        string = string[2:].split('_')
        self._next_word_gpos = self.__str2str(string[0])
        self._next_word_num_syll = self.__str2int(string[1])

    def __split_G(self, string):
        """Parses information about the number of syllables in the previous phrase

        :params string: string to parse
        """
        string = string[2:].split('_')
        self._prev_phrase_num_syll = self.__str2int(string[0])
        self._prev_phrase_num_words = self.__str2int(string[1])

    def __split_H(self, string):
        """Parses information about the number of syllables in the current phrase

        :params string: string to parse
        """
        string = string[2:].split('^')
        h1_2 = string[0].split('=')
        self._cur_phrase_num_syll = self.__str2int(h1_2[0])
        self._cur_phrase_num_words = self.__str2int(h1_2[1])

        string = string[1].split('|')
        h3_4 = string[0].split('=')
        self._cur_phrase_pos_cur_utterance_forward = self.__str2int(h3_4[0])
        self._cur_phrase_pos_cur_utterance_backward = self.__str2int(h3_4[0])

        self._cur_phrase_TOBI_endtone = self.__str2str(string[1])

    def __split_I(self, string):
        """Parses information about the number of syllables in the current phrase

        :params string: string to parse
        """
        string = string[2:].split('=')
        self._next_phrase_num_syll = self.__str2int(string[0])
        self._next_phrase_num_words = self.__str2int(string[1])

    def __split_J(self, string):
        """Parses information about the number of syllables in this utterance

        :params string: string to parse
        """
        regex = re.compile(r'J:(\d+)\+(\d+)-(\d+)')
        m = regex.match(string)
        self._cur_utterance_num_syll = int(m.group(1))
        self._cur_utterance_num_words = int(m.group(2))
        self._cur_utterance_num_phrases = int(m.group(3))

    def __char2bool(self, char):
        """Converts a character to a boolean value

        This helper method converts a given character into a boolean value or
        returns None if the value is not existing (marked as 'x').

        :params char: character to convert
        :returns: boolean value of that character
        """
        if char != 'x':
            return bool(int(char))
        else:
            return None

    def __str2int(self, string):
        """Converts a string to an integer value

        This helper method converts a given character into an integer value or
        returns None if the value is not existing (marked as 'x').

        :params string: string to convert
        :returns: boolean value of that character
        """
        if string != 'x':
            return int(string)
        else:
            return None

    def __str2str(self, string):
        """Checks if the given string is valid

        This helper method checks if a string is valid, it returns None if the
        value is not existing (marked as 'x').

        :params string: character to convert
        :returns: given string value if valid
        """
        if string != 'x':
            return string
        else:
            return None

    @property
    def LL(self):
        """Get the phoneme identity before the previous phoneme."""
        return self._LL

    @property
    def L(self):
        """Get the previous phoneme identity."""
        return self._L

    @property
    def C(self):
        """Get the current phoneme identity."""
        return self._C

    @property
    def R(self):
        """Get the next phoneme identity."""
        return self._R

    @property
    def RR(self):
        """Get the phoneme after the next phoneme identity."""
        return self._RR

    @property
    def p1(self):
        """Get the phoneme identity before the previous phoneme."""
        return self._LL

    @property
    def p2(self):
        """Get the previous phoneme identity."""
        return self._L

    @property
    def p3(self):
        """Get the current phoneme identity."""
        return self._C

    @property
    def p4(self):
        """Get the next phoneme identity."""
        return self._R

    @property
    def p5(self):
        """Get the phoneme after the next phoneme identity."""
        return self._RR

    @property
    def p6(self):
        """Get position of the current phoneme identity in the current syllable (forward)."""
        return self._cur_phoneme_id_pos_forward

    @property
    def p7(self):
        """Get position of the current phoneme identity in the current syllable (backward)."""
        return self._cur_phoneme_id_pos_backward

    @property
    def a1(self):
        """Get whether the previous syllable stressed or not."""
        return self._prev_syll_stressed

    @property
    def a2(self):
        """Get whether the previous syllable accented or not."""
        return self._prev_syll_accented

    @property
    def a3(self):
        """Get number of phonemes in the previous syllable."""
        return self._prev_syll_phoneme_num

    @property
    def b1(self):
        """Get whether the current syllable stressed or not."""
        return self._cur_syll_stressed

    @property
    def b2(self):
        """Get whether the current syllable accented or not."""
        return self._cur_syll_accented

    @property
    def b3(self):
        """Get number of phonemes in the current syllable."""
        return self._cur_syll_phoneme_num

    @property
    def b4(self):
        """Get position of the current syllable in the current word (forward)."""
        return self._cur_syll_pos_current_word_forward

    @property
    def b5(self):
        """Get position of the current syllable in the current word (backward)."""
        return self._cur_syll_pos_current_word_backward

    @property
    def b6(self):
        """Get position of the current syllable in the current phrase (forward)."""
        return self._cur_syll_pos_cur_phrase_forward

    @property
    def b7(self):
        """Get position of the current syllable in the current phrase (backward)."""
        return self._cur_syll_pos_cur_phrase_backward

    @property
    def b8(self):
        """Get the number of stressed syllables before the current syllable in the current phrase."""
        return self._cur_syll_num_stressed_sylls_before_cur_phrase

    @property
    def b9(self):
        """Get the number of stressed syllables after the current syllable in the current phrase."""
        return self._cur_syll_num_stressed_sylls_after_cur_phrase

    @property
    def b10(self):
        """Get the number of accented syllables before the current syllable in the current phrase."""
        return self._cur_syll_num_accented_sylls_before_cur_phrase

    @property
    def b11(self):
        """Get the number of accented syllables after the current syllable in the current phrase."""
        return self._cur_syll_num_accented_sylls_after_cur_phrase

    @property
    def b12(self):
        """Get the distance per syllable from the previous stressed syllable to the current syllable."""
        return self._cur_syll_distance_prev_stressed_syll

    @property
    def b13(self):
        """Get the distance per syllable from the current syllable to the next stressed syllable."""
        return self._cur_syll_distance_next_stressed_syll

    @property
    def b14(self):
        """Get the distance per syllable from the previous accented syllable to the current syllable."""
        return self._cur_syll_distance_prev_accented_syll

    @property
    def b15(self):
        """Get the distance per syllable from the current syllable to the next accented syllable."""
        return self._cur_syll_distance_next_accented_syll

    @property
    def b16(self):
        """Get name of the vowel of the current syllable."""
        return self._cur_syll_vowel

    @property
    def c1(self):
        """Get whether the next syllable stressed or not."""
        return self._next_syll_stressed

    @property
    def c2(self):
        """Get whether the next syllable accented or not."""
        return self._next_syll_accented

    @property
    def c3(self):
        """Get the number of phonemes in the next syllable."""
        return self._next_syll_num_phonems

    @property
    def d1(self):
        """Get gpos (guess part-of-speech) of the previous word."""
        return self._prev_word_gpos

    @property
    def d2(self):
        """Get the number of syllables in the previous word."""
        return self._prev_word_num_syll

    @property
    def e1(self):
        """Get gpos (guess part-of-speech) of the current word."""
        return self._cur_word_gpos

    @property
    def e2(self):
        """Get the number of syllables in the current word."""
        return self._cur_word_num_syll

    @property
    def e3(self):
        """Get position of the current word in the current phrase (forward)."""
        return self._cur_word_pos_cur_phrase_forward

    @property
    def e4(self):
        """Get position of the current word in the current phrase (backward)."""
        return self._cur_word_pos_cur_phrase_backward

    @property
    def e5(self):
        """Get the number of content words before the current word in the current phrase."""
        return self._cur_word_num_content_words_cur_phrase_before

    @property
    def e6(self):
        """Get the number of content words after the current word in the current phrase."""
        return self._cur_word_num_content_words_cur_phrase_after

    @property
    def e7(self):
        """Get the distance per word from the previous content word to the current word."""
        return self._cur_word_distance_prev_content_word

    @property
    def e8(self):
        """Get the distance per word from the current word to the next content word."""
        return self._cur_word_distance_next_content_word

    @property
    def f1(self):
        """Get gpos (guess part-of-speech) of the next word."""
        return self._next_word_gpos

    @property
    def f2(self):
        """Get the number of syllables in the next word."""
        return self._next_word_num_syll

    @property
    def g1(self):
        """Get the number of syllables in the previous phrase."""
        return self._prev_phrase_num_syll

    @property
    def g2(self):
        """Get the number of words in the previous phrase."""
        return self._prev_phrase_num_words

    @property
    def h1(self):
        """Get the number of syllables in the current phrase."""
        return self._cur_phrase_num_syll

    @property
    def h2(self):
        """Get the number of words in the current phrase."""
        return self._cur_phrase_num_words

    @property
    def h3(self):
        """Get position of the current phrase in this utterance (forward)."""
        return self._cur_phrase_pos_cur_utterance_forward

    @property
    def h4(self):
        """Get position of the current phrase in this utterance (backward)."""
        return self._cur_phrase_pos_cur_utterance_backward

    @property
    def h5(self):
        """Get TOBI endtone of the current phrase."""
        return self._cur_phrase_TOBI_endtone

    @property
    def i1(self):
        """Get the number of syllables in the next phrase."""
        return self._next_phrase_num_syll

    @property
    def i2(self):
        """Get the number of words in the next phrase."""
        return self._next_phrase_num_words

    @property
    def j1(self):
        """Get the number of syllables in this utterance."""
        return self._cur_utterance_num_syll

    @property
    def j2(self):
        """Get the number of words in this utterance."""
        return self._cur_utterance_num_words

    @property
    def j3(self):
        """Get the number of phrases in this utterance."""
        return self._cur_utterance_num_phrases

    @property
    def triphone(self):
        """Get current triphone"""
        return [self.p2, self.p3, self.p4]

    @property
    def quinphone(self):
        """Get current triphone"""
        return [self.p1, self.p2, self.p3, self.p4, self.p5]

    def print_phone(self, values_only=False):
        members = filter(lambda x: not (x.startswith('_') or x == 'original_line' or x == 'number'), self.__dict__)
        members.sort()
        # put varibles starting with p in front
        members = members[-7:] + members[0:-7]
        # order b10 to b16 correctly
        tmp = members[10:17]
        [members.remove(x) for x in tmp]
        members = members[:19] + tmp + members[19:]

        print('\n#######################################################################')
        if self.number:
            print('Phone Nr.: {:d}'.format(self.number))
        print('Start: {:6.2f}'.format(self.begin))
        print('End:   {:6.2f}\n'.format(self.end))
        for i in members:
            if values_only:
                if getattr(self, i.replace('_help', '')) is None:
                    continue

            form = '{:8s} {:s}'.format(str(getattr(self, i.replace('_help', ''))), self.__dict__[i])
            print(form)