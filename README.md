# InclusionReferencesKG

This is the implementation for Lukas Rossi's Bachelor's Thesis
"Inclusion of Reference Information in EU Regulations using Knowledge Graphs".


## Installation

It is recommended to use [Anaconda](https://www.anaconda.com/) to manage the dependencies.
Simply use: 

```console
conda env create -f environment.yml
```

to create the environment from the environment file. This will install all requirements and activate the correct environment.

Make sure the correct environment is selected by using
```console
conda activate InclusionReferencesKG
```
when running from a console or selecting 


### spaCy

Spacy requires additional downloads which can be done from the console (with an active Anaconda environment):

```console
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_trf
python -m spacy download en_core_web_sm
```

The same goes for coreferee:

```console
python -m coreferee install en
```








