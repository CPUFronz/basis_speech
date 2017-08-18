# Tools Installation

### Pre-Requisites
[Download version 3.4.1 of HTK](http://htk.eng.cam.ac.uk/download.shtml) into this folder. In order to do so you have to sign-up at their site.

Install the necessary tools:
```bash
apt-get install build-essential tcsh wget
```


### HTK and HTS

```bash
wget http://hts.sp.nitech.ac.jp/archives/2.3/HTS-2.3_for_HTK-3.4.1.tar.bz2
mkdir -p ../tools
cd ../tools
tar -xzf ../installers/HTK-3.4.1.tar.gz
mkdir HTS-2.3_for_HTK-3.4.1
cd HTS-2.3_for_HTK-3.4.1
tar -xjf ../../installers/HTS-2.3_for_HTK-3.4.1.tar.bz2
cd ..
cd htk
patch -f -p1 -d . < ../HTS-2.3_for_HTK-3.4.1/HTS-2.3_for_HTK-3.4.1.patch
./configure --prefix "$(pwd)/../build/HTK"
make
make install
cd ../../installers
```

### Festival & Speech Tools

```
wget http://festvox.org/packed/festival/2.4/festival-2.4-release.tar.gz
wget http://festvox.org/packed/festival/2.4/speech_tools-2.4-release.tar.gz
cd ../tools
tar -xzf ../installers/speech_tools-2.4-release.tar.gz
tar -xzf ../installers/festival-2.4-release.tar.gz
cd speech_tools
./configure
make
cd ../festival
./configure
make
cd ../../installers
```

### SPTK

```
wget http://downloads.sourceforge.net/sp-tk/SPTK-3.9.tar.gz
cd ../tools
tar -xzf ../installers/SPTK-3.9.tar.gz
cd SPTK-3.9
./configure --prefix "$(pwd)/../build"
make
make install
cd ../../installers
```

### hts_engine

```
wget http://downloads.sourceforge.net/hts-engine/hts_engine_API-1.10.tar.gz
cd ../tools
tar -xzf ../installers/hts_engine_API-1.10.tar.gz
cd hts_engine_API-1.10
./configure
make
cd ../../installers
```

### HTS Demo

```bash
wget http://hts.sp.nitech.ac.jp/archives/2.3/HTS-demo_CMU-ARCTIC-SLT.tar.bz2
cd ../tools
tar -xjf ../installers/HTS-demo_CMU-ARCTIC-SLT.tar.bz2
cd HTS-demo_CMU-ARCTIC-SLT
./configure \
    --with-fest-search-path="$(pwd)"/../festival/examples \
    --with-sptk-search-path="$(pwd)"/../build/bin \
    --with-hts-search-path="$(pwd)"/../build/HTK/bin \
    --with-hts-engine-search-path="$(pwd)"/../hts_engine_API-1.10/bin
make
```

### Python 3

I highly recommend useing Miniconda (https://conda.io) for encapsulating the Python environment and to make sure to have the same versions of Python and libraries.

Downloading the Miniconda installation shell script:

```bash
cd installers
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

(or look at https://conda.io/miniconda.html for other options).

Run it (no sudo required):

```bash
bash Miniconda3-latest-Linux-x86_64.sh
```

It will ask you where it should install Miniconda. You can either go with the default (`~/miniconda3`) or put it into a subdirectory of this project's tree, e.g., `.../tools/miniconda3`.

It will also ask you whether or not it should add things to your `~/.bashrc`.  Choose what you prefer, but be aware of the reults:

* **Answering no** means that you will always have to specify the path to your conda installation when you create/delete/activate conda environments, e.g.: `~/miniconda3/bin/conda create -n my_env python`
`source ~/miniconda3/bin/activate my_env`
* **Answering yes** means that you can instead just say
`conda create -n my_env`
`source activate my_env`
**but** it will also change the default `python` interpreter, the default `pip`, etc. for your user!

Create an environment based on the file `environment.yml` stored in this directory (`.../basis_speech/installers/`):

```bash
conda env create -f installers/environment.yml # or ~/miniconda3/bin/conda env create -f installers/environment.yml
```

To activate the environment:

```bash
source activate basis # or source ~/miniconda3/bin/activate basis
```

While activated, "install" the root directory of this git repository in editable/development mode:

```bash
pip install -e .../basis_speech
```
