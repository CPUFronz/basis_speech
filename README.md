# Learning of Basis Function Coefficients for Computer-generated Speech

## About
This is the code for my student's project "Supervised Learning of Basis Function Coefficients for Computer-generated Speech". The project was about investigating a new method how to predict spectral parameters for speech synthesis. First these spectral parameters are encoded as coefficients of basis functions (as legendre polynomials), then these basis function coefficients are used for training machine learning models on those coefficients and the corresponding phones.

## Installation
See [README.md](installers/README.md) for the installation instructions.

## Usage
To get started just run the file [run_all.py](basis_speech/run_all.py): `python3 run_all.py`. If you want to run a specific machine learning model start either [gm_fitting.py](basis_speech/gm_fitting.py) or [regression.py](basis_speech/regression.py). If you want to test the encoding just runb [bfcr.py](basis_speech/bfcr.py).

## Background
Wikipedia is always a good start (https://en.wikipedia.org/wiki/Speech_synthesis).
Dietmar's master's thesis (http://schabus.xyz/download/masters-thesis/) and PhD thesis (http://schabus.xyz/download/dissertation/) also both contain introductions to the problem of speech synthesis.

### Data

The website for HTS (http://hts.sp.nitech.ac.jp/?Download), an HMM-based speech synthesis system, provides a Speaker-dependent training demo for English, which includes data.
See the README.md in the `installers` directory for instructions to run the demo.

After the demo has run,  all data relevant to us is present in `tools/HTS-demo_CMU-ARCTIC-SLT/data/`

#### Recorded Audio

Directory: `raw`
The speech recordings are provided in the form of raw files (48000 Hz, Signed 16-bit PCM, Little Endian, Mono).
Audacity (http://www.audacityteam.org/, `apt-get install audacity`) can play them, after they have been imported via File -> Import -> Raw Data

The `play` command, which is part of SoX (http://sox.sourceforge.net/, `apt-get install sox`) can also play them, like this:

```bash
play -t raw -r 48k -e signed -b 16 -c 1 cmu_us_arctic_slt_a0001.raw
```

SoX can also convert them to wave files, which are a bit more convenient:

```bash
sox -t raw -r 48k -e signed -b 16 -c 1 cmu_us_arctic_slt_a0001.raw cmu_us_arctic_slt_a0001.wav
```

#### Text

Directory: `txt`

The text (in standard English orthography) of the recordings.

```bash
$ cat txt/cmu_us_arctic_slt_a0001.txt
Author of the danger trail, Philip Steels, etc.
```

#### Labels

Directory: `labels/mono`, `labels/full` and `labels/gen`

**Mono label files** contain one phone (speech sound) per line, with the start and end times:

```bash
$ head -n5 labels/mono/cmu_us_arctic_slt_a0001.lab
         0     620000 pau
    620000    1807500 pau
   1807500    3432500 ao
   3432500    4557500 th
   4557500    6182500 er
```

The time values need to be divided by 10^7 to obtain seconds (`1807500 / 1e7 == 0.18075`).
In this example, the first phone ("ao") of the first word of the utterance ("author") begins at 0.18075 seconds and ends at 0.3432 seconds.

**Full-context label files** additionally specify the context of the phone: its left and right neighbors, and a whole lot of additional information (which is not so human-friendly) like is this phone in a stressed syllable or not, how far away is it from the beginning/end of the word/sentence, ...

```bash
$ head -n5 labels/full/cmu_us_arctic_slt_a0001.lab
         0     620000 x^x-pau+pau=ao@x_x/A:x_x_x/B:x-x-x@x-x&x-x#x-x$x-x!x-x;x-x|x/C:x+x+x/D:x_x/E:x+x@x+x&x+x#x+x/F:x_x/G:x_x/H:x=x^x=x|x/I:x=x/J:14+8-2
    620000    1807500 x^pau-pau+ao=th@x_x/A:x_x_x/B:x-x-x@x-x&x-x#x-x$x-x!x-x;x-x|x/C:1+1+2/D:x_x/E:x+x@x+x&x+x#x+x/F:content_2/G:x_x/H:x=x^x=x|x/I:7=5/J:14+8-2
   1807500    3432500 pau^pau-ao+th=er@1_2/A:x_x_x/B:1-1-2@1-2&1-7#0-3$0-2!x-2;x-4|0/C:0+0+1/D:x_x/E:content+2@1+5&0+2#x+3/F:in_1/G:x_x/H:7=5^1=2|L-L%/I:7=3/J:14+8-2
   3432500    4557500 pau^ao-th+er=ah@2_1/A:x_x_x/B:1-1-2@1-2&1-7#0-3$0-2!x-2;x-4|0/C:0+0+1/D:x_x/E:content+2@1+5&0+2#x+3/F:in_1/G:x_x/H:7=5^1=2|L-L%/I:7=3/J:14+8-2
   4557500    6182500 ao^th-er+ah=v@1_1/A:1_1_2/B:0-0-1@2-1&2-6#1-3$1-2!1-1;1-3|0/C:1+0+2/D:x_x/E:content+2@1+5&0+2#x+3/F:in_1/G:x_x/H:7=5^1=2|L-L%/I:7=3/J:14+8-2
```

See `tools/HTS-demo_CMU-ARCTIC-SLT/data/lab_format.pdf` for a detailed description.

The files in `labels/gen` are also full-context label files, they are used in the demo to generate new speech.

#### Extracted Features

The directories `mgc` and `lf0` contain the extracted speech features (mel-generalized [cepstrum](https://en.wikipedia.org/wiki/Cepstrum), i.e., spectral information, and $log(F_0)$, i.e., logarithm of [fundamental frequency](https://en.wikipedia.org/wiki/Fundamental_frequency)).

The `lf0`s are 1-dimensional, the `mgc`s are 35-dimensional:

```bash
$ grep '^MGCORDER' data/Makefile
MGCORDER   = 34   # order of MGC analysis
```

Both kinds contain binary float32 values, i.e., in Python we can read them in as follows:

```python
import numpy
mgc = numpy.fromfile('mgc/cmu_us_arctic_slt_a0001.mgc', dtype=numpy.float32).reshape(-1, 35)
lf0 = numpy.fromfile('lf0/cmu_us_arctic_slt_a0001.lf0', dtype=numpy.float32)
```
