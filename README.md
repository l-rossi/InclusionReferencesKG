# InclusionReferencesKG

This is the implementation for Lukas Rossi's Bachelor's Thesis
"Inclusion of Reference Information in EU Regulations using Knowledge Graphs".


## Installation

### Requirements
The project works best with a [CUDA](https://docs.nvidia.com/cuda/) installation
for improved performance.

### Anaconda (GPU)

It is recommended to use [Anaconda](https://www.anaconda.com/) to manage the dependencies.
Simply use: 

```console
conda env create -f environment.yml
```

to create the environment from the environment file. This will install all requirements and activate the correct environment.

Make sure the correct environment is selected by using:
```console
conda activate InclusionReferencesKG
```
and/or selecting the appropriate virtual environment in you IDE.

The environment assumes the presence of a CUDA 11.6 installation. If an older
version is present one may replace the cudatoolkit package with an older version:
```
conda remove torchvision torchaudio cudatoolkit=11.3
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch
```

### Anaconda (CPU)

If CUDA is not available, the CPU can be used:

```console
conda env create -f environment-cpu.yml
```

### spaCy

Spacy requires additional downloads which can be done from the console (with an active Anaconda environment):

```console
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_trf
python -m spacy download en_core_web_sm
```

(``en_core_web_sm`` is not required if the fast option for creating knoweldge graphs is not used.)

The same goes for coreferee:

```console
python -m coreferee install en
```








