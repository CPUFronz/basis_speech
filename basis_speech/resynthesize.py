#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Diemar Schabus
@author: Franz Papst
"""

import argparse
import logging
from os.path import dirname, join, realpath
import shutil
import subprocess
import tempfile
import os
import struct

import config

logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger('resynthesize')
toolspath = realpath(join(dirname(__file__), '..', 'tools'))
PERL       = '/usr/bin/perl'
SOPR       = toolspath + '/build/bin/sopr'
EXCITE     = toolspath + '/build/bin/excite'
DFS        = toolspath + '/build/bin/dfs'
VOPR       = toolspath + '/build/bin/vopr'
MGLSADF    = toolspath + '/build/bin/mglsadf'
X2X        = toolspath + '/build/bin/x2x'
RAW2WAV    = toolspath + '/build/bin/raw2wav'
makefilter = toolspath + '/HTS-demo_CMU-ARCTIC-SLT/data/scripts/makefilter.pl'

def resynthesize(mgc, lf0_file, out_file):
    """Creates a *.wav file for a given mgc matrix and lf0 file.

    This function is a wrapper for the resynthesize_from_files() function. It
    takes a mgc matrix and creates a temprary mgc file which is used together
    with the given lf0 file to create a *.wav file

    :params mgc: the mgc matrix for creating the *.wav file
    :params lf0_file: the lf0 file for creating the *.wav file
    :params out_file: name of the created *.wav file
    """
    tmp = tempfile.TemporaryDirectory()
    tmp_mgc = tmp.name + '/mgc.npy'

    with open(tmp_mgc, 'wb') as f:
        for i in mgc.flatten():
            f.write(struct.pack('f', i))

    path = os.path.dirname(out_file)
    if not os.path.exists(path):
            os.makedirs(path)

    resynthesize_from_files(tmp_mgc, lf0_file, out_file)


def resynthesize_from_files(mgc_file, lf0_file, out_file):
    """Creates a *.wav file from a given mgc and lf0 file.

    This function takes a mgc file and a lf0 file and calls all the tools for
    creating a *.wav files from those two files.

    :params mgc: the mgc matrix for creating the *.wav file
    :params lf0_file: the lf0 file for creating the *.wav file
    :params out_file: name of the created *.wav file
    """
    logger.debug('Starting resynthesis\n' +
        '    mgc_file:  %s\n' +
        '    lf0_file:  %s\n' +
        '    out_file:  %s\n' +
        '    toolspath: %s\n',
        mgc_file, lf0_file, out_file, toolspath)

    tmpd = tempfile.TemporaryDirectory()
    logger.debug('Temporary directory: %s\n', tmpd.name)

    # convert log F0 to pitch
    # $SOPR -magic -1.0E+10 -EXP -INV -m $sr -MAGIC 0.0 $lf0 > pitch.pit
    pitch_file = tmpd.name + '/pitch.pit'
    line = SOPR + ' -magic -1.0E+10 -EXP -INV -m %d -MAGIC 0.0 %s' % (
        config.SAMPFREQ, lf0_file)
    logger.debug('Calling subprocess:\n    %s\n', line)
    with open(pitch_file, 'wb') as f:
        p = subprocess.Popen(line.split(), stdout=f)
    p.wait()

    # make filters
    # $PERL $makefilter $sr 0
    # $PERL $makefilter $sr 1
    line = '%s %s %d 0' % (PERL, makefilter, config.SAMPFREQ)
    logger.debug('Calling subprocess:\n    %s\n', line)
    lfil = subprocess.check_output(line.split()).decode('utf-8')
    line = '%s %s %d 1' % (PERL, makefilter, config.SAMPFREQ)
    logger.debug('Calling subprocess:\n    %s\n', line)
    hfil = subprocess.check_output(line.split()).decode('utf-8')

    # generate excitation
    # $SOPR -m 0 pitch.pit | $EXCITE -n -p $fs | $DFS -b $hfil > unv.unv
    unv_file = tmpd.name + '/unv.unv'
    line = SOPR + ' -m 0 ' + pitch_file
    logger.debug('Calling subprocess:\n    %s\n', line)
    p1 = subprocess.Popen(line.split(), stdout=subprocess.PIPE)
    line = EXCITE + ' -n -p %d' % config.FRAMESHIFT
    logger.debug('Calling subprocess:\n    %s\n', line)
    p2 = subprocess.Popen(line.split(), stdin=p1.stdout, stdout=subprocess.PIPE)
    line = DFS + ' -b ' + hfil
    logger.debug('Calling subprocess:\n    %s\n', line)
    with open(unv_file, 'wb') as f:
        p3 = subprocess.Popen(line.split(), stdin=p2.stdout, stdout=f)
    p3.wait()

    # synthesize raw waveform
    # $EXCITE -n -p $fs pitch.pit |
    #     $DFS -b $lfil |
    #     $VOPR -a unv.unv |
    #     $MGLSADF -P 5 -m $MGCORD -p $fs -a $fw -c $gm $mgc |
    #     $X2X +fs -o > $out
    raw_file = tmpd.name + '/out'
    line = EXCITE + ' -n -p %d %s' % (config.FRAMESHIFT, pitch_file)
    logger.debug('Calling subprocess:\n    %s\n', line)
    p1 = subprocess.Popen(line.split(), stdout=subprocess.PIPE)
    line = DFS + ' -b ' + lfil
    logger.debug('Calling subprocess:\n    %s\n', line)
    p2 = subprocess.Popen(line.split(), stdin=p1.stdout, stdout=subprocess.PIPE)
    line = VOPR + ' -a ' + unv_file
    logger.debug('Calling subprocess:\n    %s\n', line)
    p3 = subprocess.Popen(line.split(), stdin=p2.stdout, stdout=subprocess.PIPE)
    line = MGLSADF + ' -P 5 -m %d -p %d -a %f -c %d %s' % (
        config.MGCORD, config.FRAMESHIFT, config.FREQWARP, config.GAMMA,
        mgc_file)
    logger.debug('Calling subprocess:\n    %s\n', line)
    p4 = subprocess.Popen(line.split(), stdin=p3.stdout, stdout=subprocess.PIPE)
    line = X2X + ' +fs -o'
    logger.debug('Calling subprocess:\n    %s\n', line)
    with open(raw_file, 'wb') as f:
        p5 = subprocess.Popen(line.split(), stdin=p4.stdout, stdout=f)
    p5.wait()

    # convert to wav file
    # $RAW2WAV -s " . ( $sr / 1000 ) . " $out";
    # copy raw2wav to /tmp/ (ironically needed for raw2wav, removed automatically)
    shutil.copy(RAW2WAV, '/tmp/raw2wav')
    # add toolspath/build/bin to path, needed by raw2wav
    new_env = os.environ.copy()
    new_env['PATH'] += ':' + toolspath + '/build/bin'
    line = RAW2WAV + ' -s %d %s' % (config.SAMPFREQ / 1000, raw_file)
    logger.debug('Calling subprocess:\n    %s\n', line)
    p = subprocess.Popen(line.split(), env=new_env)
    p.wait()
    wav_file = raw_file + '.wav' # raw2wav adds .wav extension

    # copy final wav file from temporary directory to destination
    logger.debug('Copying %s to %s', wav_file, out_file)
    shutil.copy(wav_file, out_file)


if __name__ == '__main__':
    # resynthesizes a *.wav file from a given mgc and lf0 file
    parser = argparse.ArgumentParser()
    parser.add_argument('mgc_file')
    parser.add_argument('lf0_file')
    parser.add_argument('out_file')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        fh = logging.FileHandler('resynthesize.log')
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

        logger.setLevel(logging.DEBUG)
        print()

    resynthesize(args.mgc_file, args.lf0_file, args.out_file)
