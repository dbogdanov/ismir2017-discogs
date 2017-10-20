# ISMIR-2017-Discogs: Dataset, code for analysis and results
This repository contains:

- Pre-processed dataset of release metadata from the Discogs database
- Useful code for analysis of release metadata using this dataset
- Additional materials for the paper ["Quantifying music trends and facts using editorial metadata from the Discogs database" (Bogdanov & Serra, ISMIR-2017)](http://mtg.upf.edu/node/3828). 

Please, cite this paper if you are using our dataset and code.
 
See [**examples of metadata analysis that can be done**](examples/) using metadata from Discogs.



## Pre-processed dataset of release metadata from Discogs
- Pre-processed release metadata dump in [hdf format](https://drive.google.com/file/d/0B9efYsv7Y7gpWmVuUWI0RXQtUFE/view?usp=sharing) (pandas DataFrame).
- Pre-processed release metadata dump in [json format](https://drive.google.com/file/d/0B9efYsv7Y7gpVmJEQnYxNXBhaHM/view?usp=sharing) (every line in the file is a json dictionary).
- [Original data dumps in XML format](https://data.discogs.com)

## Code for data pre-processing and analysis
This is the code that we used to create our release dataset and for our example studies presented in the ISMIR-2017's paper.

### Dependencies
Run ```pip install -r requirements.txt``` to install required dependencies.

### Configuration
- ```config.py```: basic configuration script, contains some global variables (like filenames) used by other scripts

### Dataset creation and analysis
- ```preprocess_releases_xml_to_json.py```: downloads the original XML dump archive and converts a subset of its metadata fields to a json dump.
- ```preprocess_releases_json_to_hdf_pandas.py```: further simplifies the metadata removing and recoding some fields, and outputs a HDF file with a pandas DataFrame.
- ```analyze.py```: a collection of useful functions for analysis of the dataset.
