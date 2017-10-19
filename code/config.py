#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configure filenames used to store and process dump for analysis
import yaml
import seaborn
import matplotlib
import matplotlib.pyplot as plt

dump_url = 'https://discogs-data.s3-us-west-2.amazonaws.com/data/2017/discogs_20170401_releases.xml.gz'
dump_gz = '../data/discogs_20170401_releases.xml.gz'
dump_json = '../data/discogs_20170401_releases.json.dump'
dump_pandas = '../data/discogs_20170401_releases.100.hdf'

results_stats = '../results/data_stats.pickle'
results_duration = '../results/data_duration.pickle'

# Discogs genre tree
GENRE_TREE = yaml.load(open('../taxonomy/discogs_taxonomy.yaml'))

# The list of genre to ignore in the analysis.
# For the sake of simplicity, we don't want some genres that are very
# infrequent anyways.
IGNORE_GENRES = ["Brass & Military",
                 "Children's",
                 "Non-Music",
                 "Stage & Screen"]


# Some global parameters for this study
START_YEAR = 1970
END_YEAR = 2016
PLOT_TITLES = True


# Plotting helper function
def prepare_colors(number):
    return seaborn.color_palette("hls", number)

# configure plotting style
def set_style():
    plt.style.use(['seaborn-white', 'seaborn-paper'])
    matplotlib.rc("font", family="Times New Roman")
