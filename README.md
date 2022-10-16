# InclusionReferencesKG

This is the implementation for Lukas Rossi's bachelor's thesis
"Inclusion of Reference Information in EU Regulations using Knowledge Graphs".


## Installation

### Requirements
The project works either using
CPU exclusive packages or with a [CUDA](https://docs.nvidia.com/cuda/) installation
for slightly improved performance or:

### Anaconda (GPU)

It is recommended to use [Anaconda](https://www.anaconda.com/) to manage the dependencies.
From the Anaconda Prompt or after
adding Anaconda your Path, simply use: 

```console
conda env create -f environment.yml
```

to create the environment from the environment file. This will install all requirements and activate the correct environment.

Make sure the correct **environment is activated** by using:
```console
conda activate InclusionReferencesKG
```
and/or selecting the appropriate virtual environment in you IDE.

The environment assumes the presence of a CUDA 11.6 installation. If an older
version is present one may replace the cudatoolkit package with an older version:
```
conda remove torchvision torchaudio cudatoolkit=11.6
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch
```

### Anaconda (CPU)

If CUDA is not available, the CPU can be used:

```console
conda env create -f environment_cpu.yml
```

Again, make sure the correct environment is selected by using:
```console
conda activate InclusionReferencesKG
```

### spaCy

Spacy and coreferee require additional downloads which can be done from the console (with an active Anaconda environment):

```console
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_trf
python -m spacy download en_core_web_sm
python -m coreferee install en
```

(``en_core_web_sm`` is not required if the fast option for creating knoweldge graphs is not used.)


You might need to restart your IDE after installation.


## Usage

**We assume the working directory to be './inclusionreferenceskg/'**

We recommend having a look at ``./src/main.py`` for an overview of the capabilities of this codebase. It shows how a document can be selected for processing and a knowledge graph can be created.

Running ``./src/main.py`` will create a visual representation of a knowledge graph and save it to ``./output/graphs/ExampleKG.gv.svg``. Make sure the InclusionReferencesKG environment is active when running:

```console
conda activate InclusionReferencesKG
python ./src/main.py
```

on Windows or

```console
conda activate InclusionReferencesKG
python3 ./src/main.py
```

on Linux.
Doing so will print some warnings about references not being resolved. These
can be dismissed.

The evaluation script can be found in the ``evaluation`` package. Each file with the prefix ``evaluate_`` should be run as its own script:

```
conda activate InclusionReferencesKG
python ./src/evaluate_reference_detector.py
python ./src/evaluate_reference_resolver.py
python ./src/evaluate_kg_creation.py
```

on Windows or

```
conda activate InclusionReferencesKG
python3 ./src/evaluate_reference_detector.py
python3 ./src/evaluate_reference_resolver.py
python3 ./src/evaluate_kg_creation.py
```

on Linux.


