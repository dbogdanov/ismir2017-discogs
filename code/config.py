#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Configure filenames used to store and process dump for analysis
import yaml
import seaborn

dump_url = 'https://discogs-data.s3-us-west-2.amazonaws.com/data/2017/discogs_20170401_releases.xml.gz'
dump_gz = '../data/discogs_20170401_releases.xml.gz'
dump_json = '../data/discogs_20170401_releases.json.dump'
dump_pandas = '../data/discogs_20170401_releases.100.hdf'

results_stats = '../results/data_stats.pickle'
results_duration = '../results/data_duration.pickle'
results_duration_evolution = '../results/data_duration_evolution.pickle'
results_formats = '../results/data_formats_evolution.pickle'
results_formats_styles = '../results/data_formats_evolution_styles.pickle'
results_genre_trends = '../results/data_genre_trends.pickle'
results_style_trends = '../results/data_style_trends.pickle'
results_genre_cooccurrences = '../results/results_genre_cooccurrences.pickle'
results_genre_cooccurrences_by_year = '../results/results_genre_cooccurrences_by_year.pickle'

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
PLOT_LARGE = False


# Plotting helper function
def prepare_colors(number):
    return seaborn.color_palette("hls", number)

