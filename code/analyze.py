#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas
import matplotlib.pyplot as plt
import numpy as np
import scipy

import pprint
import pickle

from adjustText import adjust_text

from config import *


# Functions for selecting data

def select_genre(data, genre):
    """Return all releases annotated with the specified genre"""
    return data[data['genres'].apply(lambda x: genre in x)]


def select_style(data, style):
    """Return all releases annotated with the specified style"""
    return data[data['styles'].apply(lambda x: style in x)]


def select_only_genre(data, genre):
    """Return all releases annotated solely with the specified genre"""
    return data[data['genres'].apply(lambda x: len(x) == 1 and genre in x)]


def select_only_style(data, style):
    """Return all releases annotated solely with the specified style"""
    return data[data['styles'].apply(lambda x: len(x) == 1 and style in x)]


def select_label(data, label):
    """Return all releases from the specified label"""
    return data[data['labels'].apply(lambda x: label in x)]


def select_artistname(data, artist):
    """Return all releases by the specified artist"""
    return data[data['artists'].apply(lambda x: artist in [a['name'] for a in x])]


def select_artistid(data, artistid):
    """Return all releases by the specified artistid"""
    return data[data['artists'].apply(lambda x: artistid in [a['id'] for a in x])]


def select_masterid(data, masterid):
    """Return all releases associated to the specified masterid"""
    return data[data['master_id'] == masterid]


def select_year(data, year):
    """Return all releases from the specified year"""
    return data[data['released'] == year]


def select_country(data, country):
    """Return all releases from the specified country"""
    return data[data['country'] == country]


def select_format(data, format):
    """Return all releases for the specified format"""
    return data[data['formats'].apply(lambda x: format in x)]


def select_tracks(data, tracks_number):
    """Return all releases with the specified number of tracks"""
    return data[data['tracks_number'] == tracks_number]


def select_unofficial(data):
    """Return all releases annotated as unofficial"""
    return data[data['unofficial'] == True]


def select_compilation(data):
    """Return all releases annotated as compilations"""
    return data[data['compilation'] == True]


def select_mixed(data):
    """Return all releases annotated as mixed"""
    return data[data['mixed'] == True]


def select_notmixed(data):
    """Return all releases not annotated as mixed"""
    return data[data['mixed'] == False]



def select(data, genre=None, style=None, format=None, year=None, country=None, tracks=None):
    """
    Return all releases from the specified genre, style, format, year, country,
    and number of tracks
    """
    selected = data
    if style:
        selected = select_style(selected, style)
        if not len(selected):
            return selected
    if genre:
        selected = select_genre(selected, genre)
        if not len(selected):
            return selected
    if format:
        selected = select_format(selected, format)
        if not len(selected):
            return selected
    if year:
        selected = select_year(selected, year)
        if not len(selected):
            return selected
    if country:
        selected = select_country(selected, country)
        if not len(selected):
            return selected
    if tracks:
        selected = select_tracks(selected, tracks)

    return selected


# Functions for unique artists analysis (TODO)
# Each unique artist is associated with a list of ids for all artist items in
# which he/she participated (TODO: get this data from the artist dump)

def select_artistids(data, artistids):
    """Return all releases matching the specified list of artistid"""
    return data[data['artists'].apply(lambda x: len(set(artistids) & set([a['id'] for a in x])) > 0)]


# Functions to gather vocabulary of genres/styles/formats/countries in data


def find_genres(data):
    """Find out all genres present in data"""
    genres = set()
    for gg in data['genres']:
        for g in gg:
            genres.add(g)
    return sorted(list(genres))


def find_styles(data):
    """Find out all styles present in data"""
    styles = set()
    for ss in data['styles']:
        for s in ss:
            styles.add(s)
    return sorted(list(styles))


def find_formats(data):
    """Find out all formats present in data"""
    formats = set()
    for ff in data['formats']:
        for f in ff:
            formats.add(f)
    return sorted(list(formats))


def find_countries(data):
    """Find out all countries present in data"""
    releases = data[pandas.notnull(data['country'])]
    countries = set()
    for c in releases['country']:
        countries.add(c)
    return sorted(list(countries))


def find_artists(data):
    """Find out all artists present in data"""
    artists = set()
    for aa in data['artists']:
        for a in aa:
            artists.add(a)
    return artists


# Functions for duration analysis

def select_with_durations(data):
    """Return all releases with tracks annotated by duration"""
    return data[pandas.notnull(data['tracks_duration_list'])]


def find_durations(data):
    """Find out all track duration values in data"""
    releases = select_with_durations(data)
    if not len(releases):
        return None
    return [d for dd in releases['tracks_duration_list'].tolist() for d in dd]


# Functions for per-year analysis


def releases_per_year(data, start_year, end_year, format=None, genre=None, style=None, country=None):
    """
    Count the number of releases from 'start_year' to 'end_year'
    from the specified format, genre, style and country
    """
    years = range(start_year, end_year+1)
    number_releases = [len(select(data, year=year, genre=genre, style=style, format=format, country=country)) for year in years]
    return years, number_releases


def artists_per_year(data, start_year, end_year, format=None, genre=None, style=None, country=None):
    """
    Count the number of artists from 'start_year' to 'end_year'
    from the specified format, genre, style and country
    """
    years = range(start_year, end_year+1)
    number_releases = [len(select(data, year=year, genre=genre, style=style, format=format, country=country)) for year in years]
    return years, number_releases
    years = range(start_year, end_year+1)
    number_artists = []
    for year in years:
        releases = select(data, year=year, genre=genre, style=style, format=format, country=country)
        artists = set()
        for aa in releases['artists']:
            for a in aa:
                artists.add(a)
        number_artists.append(len(artists))
    return years, number_artists


def tracks_per_year(data, start_year, end_year, format=None, genre=None, style=None, country=None):
    """
    Count the number of tracks from 'start_year' to 'end_year'
    from the specified format, genre, style and country
    """
    years = range(start_year, end_year+1)
    number_tracks = []
    for year in years:
        releases = select(data, year=year, genre=genre, style=style, format=format, country=country)
        try:
            number_tracks.append(releases['tracks_number'].sum())
        except:
            print len(releases)
    return years, number_tracks


# Functions for data statistics/coverage

def releases_stats(data):
    """
    Compute statistics for a dataset
    - present genres, styles, formats and countries and their total number
    - total number of releases, tracks, and artists
    - percentage of releases annotated by duration, and their total duration
    - total number of unofficial releases and tracks
    - total number of releases and tracks from compilations
    - total number of mixed releases and tracks
    """
    stats = {}

    stats['all_genres'] = find_genres(data)
    stats['all_styles'] = find_styles(data)
    stats['all_formats'] = find_formats(data)
    stats['all_countries'] = find_countries(data)

    stats['total_genres'] = len(stats['all_genres'])
    stats['total_styles'] = len(stats['all_styles'])
    stats['total_formats'] = len(stats['all_formats'])
    stats['total_countries'] = len(stats['all_countries'])

    stats['total_releases'] = len(data)
    stats['total_tracks'] = data['tracks_number'].sum()
    stats['total_artists'] = len(find_artists(data))

    stats['releases_annotated_by_duration (%)'] = 100. * data['tracks_duration'].count() / len(data)
    stats['total_duration_days'] = data['tracks_duration'].sum() / 60. / 24.
    stats['total_duration_years'] = 0.00273973 * stats['total_duration_days']

    unofficial = select_unofficial(data)
    stats['total_releases_unofficial'] = len(unofficial)
    stats['total_tracks_unofficial'] = unofficial['tracks_number'].sum()
    # stats['total_artists_unofficial'] = len(find_artists(unofficial))

    compilation = select_compilation(data)
    stats['total_releases_compilation'] = len(compilation)
    stats['total_tracks_compilatioñn'] = compilation['tracks_number'].sum()

    mixed = select_mixed(data)
    stats['total_releases_mixed'] = len(mixed)
    stats['total_tracks_mixed'] = mixed['tracks_number'].sum()

    return stats


def releases_coverage(data, data_stats=None):
    """
    Compute coverage for a dataset (percentages of releases, tracks and
    artists) in terms of genres, styles, countries and formats
    """
    if data_stats is None:
        data_stats = releases_stats(data)

    # TODO add coverage in terms of labels
    stats = {
        'coverage_genres': {
             'releases (%)': {},
             'tracks (%)': {},
             'artists (%)': {},
        },
        'coverage_styles': {
             'releases (%)': {},
             'tracks (%)': {},
             'artists (%)': {},
        },
        'coverage_countries': {
             'releases (%)': {},
             'tracks (%)': {},
             'artists (%)': {},
        },
        'coverage_formats': {
             'releases (%)': {},
             'tracks (%)': {},
             'artists (%)': {},
        },
    }

    # TODO re-factor all ugly code below

    for g in data_stats['all_genres']:
        releases = select_genre(data, g)
        stats['coverage_genres']['releases (%)'][g] = 100. * len(releases)/len(data)
        stats['coverage_genres']['tracks (%)'][g] = 100. * releases['tracks_number'].sum() / data_stats['total_tracks']
        stats['coverage_genres']['artists (%)'][g] = 100. * len(find_artists(releases)) / data_stats['total_artists']

    for s in data_stats['all_styles']:
        releases = select_style(data, s)
        stats['coverage_styles']['releases (%)'][s] = 100. * len(releases)/len(data)
        stats['coverage_styles']['tracks (%)'][s] = 100. * releases['tracks_number'].sum() / data_stats['total_tracks']
        stats['coverage_styles']['artists (%)'][s] = 100. * len(find_artists(releases)) / data_stats['total_artists']

    for c in data_stats['all_countries']:
        releases = select_country(data, c)
        stats['coverage_countries']['releases (%)'][c] = 100. * len(releases)/len(data)
        stats['coverage_countries']['tracks (%)'][c] = 100. * releases['tracks_number'].sum() / data_stats['total_tracks']
        stats['coverage_countries']['artists (%)'][c] = 100. * len(find_artists(releases)) / data_stats['total_artists']

    for f in data_stats['all_formats']:
        releases = select_format(data, f)
        stats['coverage_formats']['releases (%)'][f] = 100. * len(releases)/len(data)
        stats['coverage_formats']['tracks (%)'][f] = 100. * releases['tracks_number'].sum() / data_stats['total_tracks']
        stats['coverage_formats']['artists (%)'][f] = 100. * len(find_artists(releases)) / data_stats['total_artists']

    for type_key in ["coverage_genres", "coverage_styles", "coverage_countries", "coverage_formats"]:

        stats_tmp = [[v for k, v in stats[type_key]['releases (%)'].items()],
                     [v for k, v in stats[type_key]['tracks (%)'].items()],
                     [v for k, v in stats[type_key]['artists (%)'].items()]]

        columns = stats[type_key]['releases (%)'].keys()
        index = ['releases (%)', 'tracks (%)', 'artists (%)']
        df = pandas.DataFrame(stats_tmp, columns=columns, index=index)
        df = df.sort_values(by='releases (%)', axis=1, ascending=False)
        data_stats[type_key] = df

    return data_stats


def show_releases_coverage(coverage_df, type="genre", show_top=15):
    """
    Visualize coverage for a dataset in terms of genres, styles, countries, and
    formats given a DataFrame with coverage statistics

    - type: genre, style, country, format
    - show_top: number of top categories to show
    """
    if type == "genre":
        title = 'Genre'
    elif type == "style":
        title = 'Style'
    elif type == "country":
        title = 'Country'
    elif type == "format":
        title = 'Format'
    else:
        print("Wrong 'type' value (expected 'genre' or 'style'): %s" % type)
        return
    title += ' coverage in terms of number of releases, tracks and artists'

    coverage_df = coverage_df[list(coverage_df)[:15]]

    coverage_df.plot(kind='barh', color=prepare_colors(len(list(coverage_df))))
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    # plt.ylim([0, 100])
    if PLOT_TITLES:
        plt.title(title)

    plt.show()
    return


def coverage_countries_evolution(data,
                                 countries=['US', 'UK', 'Germany', 'Brazil'],
                                 genre=None, style=None, type='releases',
                                 title=None,
                                 start_year=START_YEAR, end_year=END_YEAR):
    """
    Visualize coverage for a dataset in terms countries by year
    - start_year and end_year define the time interval to consider
    - countries is a list of countries to plot
    - genre and style: only consider releases from those genres and styles
    - type='releases': compute coverage in terms of releases
    - type='tracks': compute coverage in terms of tracks
    - title: plot title to show
    """

    if type == 'releases':
        compute = releases_per_year
    elif type == 'tracks':
        compute = tracks_per_year

    if not title:
        title = "Number of " + type + " across years by country"
        if genre:
            title = title + " (%s)" % genre
        if style:
            title = title + " (%s)" % style

    stats = {}
    for c in countries:
        years, counts = compute(data, start_year, end_year,
                                genre=genre, style=style, country=c)
        stats[c] = counts
        stats.setdefault('years', years)

    for c, color in zip(countries, prepare_colors(len(countries))):
        stats[c] = [float('nan') if x == 0 else x for x in stats[c]]
        plt.plot(stats['years'], stats[c], label=c, color=color)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    if PLOT_TITLES:
        plt.title(title)
    plt.show()

    return stats


def coverage_genres_evolution(data,
                              genres,
                              type='releases',
                              title=None,
                              start_year=START_YEAR, end_year=END_YEAR):
    """
    Visualize coverage for a dataset in terms countries by year
    - start_year and end_year define the time interval to consider
    - countries is a list of countries to plot
    - genre and style: only consider releases from those genres and styles
    - type='releases': compute coverage in terms of releases
    - type='tracks': compute coverage in terms of tracks
    - title: plot title to show
    """

    if type == 'releases':
        compute = releases_per_year
    elif type == 'tracks':
        compute = tracks_per_year

    if not title:
        title = "Number of " + type + " across years by genre"

    stats = {}
    for g in genres:
        years, counts = compute(data, start_year, end_year, genre=g)
        stats[g] = counts
        stats.setdefault('years', years)

    for g, color in zip(genres, prepare_colors(len(genres))):
        stats[g] = [float('nan') if x == 0 else x for x in stats[g]]
        plt.plot(stats['years'], stats[g], label=g, color=color)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    if PLOT_TITLES:
        plt.title(title)
    plt.show()

    return stats


# Functions for track duration analysis

def plot_track_durations(stats, type, sortby="median",
                         top_n=None, bottom_n=None,
                         title=None,
                         shorten_stylenames=False):
    """
    Plot duration statistics. Use together with track_duration_per_genre method
    - stats - the output dict produced by the track_duration_per_genre method
    - type:
        - "genre" using all tracks annotated by any genre
        - "style" using all tracks annotated by any style
        - "genre_only" using only tracks annotated by a single genre
        - "style_only" using only tracks annotated by a single style
    - sortby: "median" - sort by median value,
              "95vs5" - sort by variability (range between 95% vs 5%)
              "iqr" -- sort by variability (IQR)
              "name" - sort by genre (style) name
    - top_n - only show top n genres (styles) ordered by 'sortby'
    - bottom_n - only show bottom n genre (styles) ordered by 'sortby'
    - shorten_stylenames: prints style name without genre name)
      (e.g., "Ambient" instead of "Electronic - Ambient")
    """

    if title is None:
        if type == "genre":
            title = "Boxplot of track durations (sec.) per genre"
        elif type == "genre_only":
            title = "Boxplot of track durations (sec.) per genre (exclusive)"
        elif type == "style":
            title = "Boxplot of track durations (sec.) per style"
        elif type == "style_only":
            title = "Boxplot of track durations (sec.) per style (exclusive)"
        else:
            print("Wrong type:", type)
            return

    if sortby == "median":
        sorted_genres = sorted([(stats[g]['median'], g) for g in stats])
    elif sortby == "95vs5":
        sorted_genres = sorted([(stats[g]['95vs5'], g) for g in stats])
    elif sortby == "iqr":
        sorted_genres = sorted([(stats[g]['iqr'], g) for g in stats])
    elif sortby == "name":
        # TODO
        pass

    if top_n and bottom_n:
        sorted_genres = sorted_genres[:bottom_n] + sorted_genres[-top_n:]
    elif top_n:
        sorted_genres = sorted_genres[-top_n:]
    elif bottom_n:
        sorted_genres = sorted_genres[:bottom_n]

    genres = [g for v, g in sorted_genres]
    values = [stats[g]['durations'] for g in genres]

    # 400 genre rows fit well into vertical size of 80 (0.2 row per 1 unit of size)
    plt.figure(figsize=(7, len(sorted_genres)*0.2))

    if type == "genre" or type == "genre_only":
        labels = ["%s (%d)" % (g, len(stats[g]['durations'])) for g in genres]
        plt.xlim([0, 25])
    elif type == "style" or type == "style_only":
        if shorten_stylenames:
            labels = ["%s (%d)" % (g[1], len(stats[g]['durations'])) for g in genres]
        else:
            labels = ["%s - %s (%d)" % (g[0], g[1], len(stats[g]['durations'])) for g in genres]
        plt.xlim([0, 40])

    plt.boxplot(values, vert=False, labels=labels, whis=[5, 95])
    if PLOT_TITLES:
        plt.title(title)
    plt.gca().xaxis.grid(True)
    plt.show()


def track_duration_per_genre(data, genres, type="genre"):
    """
    Analyze tracks durations per genre (style)
    - data: input dataframe with release information
    - type:
        - "genre" using all tracks annotated by any genre
        - "style" using all tracks annotated by any style
        - "genre_only" using only tracks annotated by a single genre
        - "style_only" using only tracks annotated by a single style
    - genres: list of genres (or styles) to include in analysis
    - skip_genres: list of genres (or styles) to exclude from analysis
    - title: plot title to show
    - shorten_stylenames: prints style name without genre name
      (e.g., "Ambient" instead of "Electronic - Ambient")

    Returns data required for plotting
    """

    if type == "genre":
        select_func = select_genre
    elif type == "genre_only":
        select_func = select_only_genre
    elif type == "style":
        select_func = select_style
    elif type == "style_only":
        select_func = select_only_style
    else:
        print("Wrong type:", type)
        return

    stats = {}
    for g in genres:
        releases = select_func(data, g)
        releases = select_with_durations(releases)
        durations = find_durations(releases)
        if durations is None:
            continue
        stats[g] = {}
        stats[g]['durations'] = durations
        stats[g]['median'] = np.median(stats[g]['durations'])
        stats[g]['95%'] = np.percentile(stats[g]['durations'], 95)
        stats[g]['5%'] = np.percentile(stats[g]['durations'], 5)
        stats[g]['95vs5'] = stats[g]['95%'] - stats[g]['5%']
        stats[g]['iqr'] = scipy.stats.iqr(stats[g]['durations'])

    return stats


def plot_track_durations_2d(stats, genres, xlim=[1, 8], ylim=[0,9], annotate=False):
    plt.figure(figsize=(12, 12))

    for genre in genres:
        styles = [s for s in stats.keys() if s[0] == genre]
        medians = [stats[s]['median'] for s in styles]
        iqrs = [stats[s]['iqr'] for s in styles]
        plt.scatter(medians, iqrs, label=genre)

        if annotate:
            texts = []
            for s, m, i in zip(styles, medians, iqrs):
                if m > 3 and m < 5 and i > 1 and i < 3:
                    continue
                plt.annotate(s[1], (m, i))

    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.gca().xaxis.grid(True)
    plt.xlabel("Median duration (mins)")
    plt.ylabel("Duration variability (mins)")
    plt.xlim(xlim)
    plt.ylim(ylim)

    if PLOT_TITLES:
        title = "Median duration vs. variability (IQR) for styles"
        plt.title(title)
    plt.show()


def plot_track_durations_evolution(stats, genres=None, start_year=START_YEAR, end_year=END_YEAR):
    """
    Plot evolution of track durations per genre by year
    - stats: the output of track_durations_evolution method
    - genres: list of genres (styles) to plot (all by default)
    """
    if genres is None:
        genres = stats.keys()

    for g, c in zip(genres, prepare_colors(len(genres))):
        years = stats[g]['year']
        plt.plot(years, stats[g]['p25'], label="25%")
        plt.plot(years, stats[g]['median'], label="50%")
        plt.plot(years, stats[g]['p75'], label="75%")

        plt.legend()
        #plt.legend(loc="upper left", bbox_to_anchor=(1,1))

        plt.xlim(plt.xlim()[0], end_year)
        
        if type(g) is tuple:
            g = "%s - %s" % (g[0], g[1])
        
        if PLOT_TITLES:
            plt.title("Duration of tracks across years" + " (" + g + ")")
        else:
            print "Duration of tracks across years", g
        plt.show()

    return


def track_durations_evolution(data, genres, type="genre", 
                              start_year=START_YEAR, end_year=END_YEAR, 
                              ignore_compilations=False):
    """
    Analyze evolution of track durations per genre by year
    - data: input dataframe with release information
    - genres: list of genres or styles to analyze
    - type: use "genre" for genres, "style" for styles
    """
    stats = {}
    for g in genres:
        if type == "genre":
            releases = select_genre(data, g)
        elif type == "style":
            releases = select_style(data, g)
        else:
            print("Wrong type: %s", type)

        if ignore_compilations:
            releases = releases[releases['compilation'] == False]

        stats[g] = {'year': [], 'median': [], 'p25': [], 'p75': []}

        for year in range(start_year, end_year+1):
            releases_year = select_year(releases, year)
            durations = find_durations(releases_year)
            if durations is None:
                continue

            stats[g]['year'] += [year]
            stats[g]['median'] += [np.median(durations)]
            stats[g]['p25'] += [np.percentile(durations, 25)]
            stats[g]['p75'] += [np.percentile(durations, 75)]

    return stats


# Functions for loading and saving dumps

def sample_release_dump(input_dump, sampled_dump, fraction):
    """
    Sample input release dump
    - fraction: the fraction of releases to sample (e.g., 0.1 is 10%)
    - input_dump: filename for the input hdf dump
    - sampled_dump: filename for the output hdf dump
    """
    print("Loading release dump from %s" % input_dump)
    data = pandas.read_hdf(input_dump)
    print("Sampling %d%% of releases" % int(fraction*100))
    data = data.sample(frac=fraction)
    print("Releases in the sample: %d" % len(data))

    print("Saving the sample dump DataFrame to %s" % sampled_dump)
    data.to_hdf(sampled_dump, 'w')
    return


def load_release_dump(input_dump):
    """
    Loads hf release dump given the filename
    """
    return pandas.read_hdf(input_dump)

# Functions for format analysis

def compare_formats(data,
                    formats=['Vinyl', 'Cassette', 'CD', 'CDr', 'File'],
                    genre=None,
                    style=None,
                    type='releases',
                    start_year=START_YEAR,
                    end_year=END_YEAR):
    """
    Analyze formats evolution.
    - data: input DataFrame with releases
    - type: measure music in terms of "releases" or "tracks"
    """
    stats = {}

    if type == 'releases':
        compute = releases_per_year
    elif type == 'tracks':
        compute = tracks_per_year

    stats['years'], stats['all'] = compute(data, start_year, end_year, genre=genre, style=style)
    for f in formats:
        _, stats[f] = compute(data, start_year, end_year, format=f, genre=genre, style=style)

    return pandas.DataFrame(stats)


def plot_compare_formats(stats, type, genre, absolute=False):
    """
    Plot results of analysis of formats
    - stats: the output of compare_formats method
    - type: "releases" or "tracks"
    - absolute: show absolute values instead of percentages
    """
    if absolute:
        plt.plot(stats['years'], stats['all'], label='All')
        for f in formats:
            plt.plot(stats['years'], stats[f], label=f)

        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))

        title = "Number of %s per format by year (%s)" % (type, genre)
        if PLOT_TITLES:
            plt.title(title)
        else:
            print(title)
    else:
        for f in formats:
            plt.plot(stats['years'], 100. * stats[f] / stats['all'], label=f)
        #plt.legend(loc="upper left", bbox_to_anchor=(1,1))
        plt.legend()
        title = "Percentage of %s per format by year (%s)" (type, genre)
        if PLOT_TITLES:
            plt.title(title)
        else:
            print(title)

    plt.show()
    return


def compare_genres(data,
                   metric='releases',
                   genres=None, styles=None, country=None, format=None,
                   start_year=START_YEAR, end_year=END_YEAR):
    """
    Analyze genre or styles evolution
    - data: input DataFrame with releases
    - type: measure music in terms of "releases", "tracks", or "artists"
    - genres: list of genres to analyze
    - styles: list of styles to analyze (genres and styles cannot be specified together)
    """
    if genres and styles:
        print("ERROR: cannot specify 'genres' and 'styles' simultaneously")
        return
    elif genres:
        genre_or_style = "genre"
    elif styles:
        genre_or_style = "style"

    if metric == 'releases':
        compute = releases_per_year
    elif metric == 'tracks':
        compute = tracks_per_year
    elif metric == 'artists':
        compute = artists_per_year

    stats = {}
    stats['years'], stats['all'] = compute(data, start_year, end_year, country=country, format=format)

    if genres:
        for g in genres:
            _, stats[g] = compute(data, start_year, end_year, genre=g, country=country, format=format)
    elif styles:
        for s in styles:
            _, stats[s] = compute(data, start_year, end_year, style=s, country=country, format=format)
        genres = styles

    return pandas.DataFrame(stats)


def plot_compare_genres(stats, metric, genres, absolute=False):
    """
    Plot results of analysis of genre or style evolution
    - stats: the output of compare_genres method
    - metric: measure music in terms of "releases", "tracks", or "artists"
    - genres: genres or styles to plot
    - absolute: show absolute values instead of percentages
    """

    # TODO some code to re-factor
    """
    if print_important and styles:
        # identify only important styles and print those
        # we only want genres that are visible in the plot, i.e., having larger area
        important_styles = sorted([(np.sum(stats[s]), s) for s in styles], reverse=True)
        important_styles = [s for c, s in important_styles]
        important_styles = [s for g,s in important_styles]
        print important_styles
        #for i in range(len(stats['years'])):
        #    top_styles = [s for st, s in sorted([(stats[s][i], s) for s in styles], reverse=True)[:5]]
        #    print stats['years'][i], [s for g, s in top_styles]
    """

    if absolute:
        #plt.plot(years, stats['all'], label='All')
        for g, c in zip(genres, prepare_colors(len(genres))):
            if g is tuple:
                str_g = "%s - %s" % (g[0], g[1])
                genre_or_style = "style"
            else:
                str_g = g
                genre_or_style = "genre"

            plt.plot(stats['years'], stats[g], label=str_g, color=c)

        title = "Number of " + metric + " per " + genre_or_style + " by year"
        if PLOT_TITLES:
            plt.title(title)
        else:
            print(title)
    else:
        for g, c in zip(genres, prepare_colors(len(genres))):
            if g is tuple:
                str_g = "%s - %s" % (g[0], g[1])
                genre_or_style = "style"
            else:
                str_g = g
                genre_or_style = "genre"

            plt.plot(stats['years'], 100. * stats[g] / stats['all'], label=str_g, color=c)

        title = "Percentage of " + metric + " per " + genre_or_style + " by year"
        if PLOT_TITLES:
            plt.title(title)
        else:
            print(title)

    plt.legend(loc="upper left", bbox_to_anchor=(1,1))
    plt.show()

# TODO add functions for regional trends (move code from my old notebook)

# Functions for genre and styles co-occurrence analysis

def rename_style(style):
    g, s = style
    return "%s - %s" % (g, s)


# TODO review this function
"""
def genre_cooccurences(data, genre, type="genre"):
    if type=="genre":
        select_func = select_genre
    elif type =="style":
        select_func = select_style
    else:
        return "ERROR"

    select = select_func(data, genre)
    stats = []
    for g in find_genre(select):
        stats.append((g, 100. * len(select_func(select, g)) / len(select)))
    return sorted(stats, key=lambda x: x[1], reverse=True)
"""


def genre_cooccurences_matrix(data, genres=None, type="genre", rename=None):
    """
    Compute a genre co-occurrence matrix
    - data: input DataFrame with releases
    - type: "genre" or "style"
    - rename: rename function for genres or styles
    """

    if type == "genre":
        find_func = find_genres
        select_func = select_genre
    elif type == "style":
        find_func = find_styles
        select_func = select_style
    else:
        print("ERROR: wrong type")

    if not genres:
        genres = find_func(data)

    result = {}

    nonempty_genres = {}
    for g in genres:
        select = select_func(data, g)
        if len(select):
            nonempty_genres[g] = select

    genres = []
    for g1 in nonempty_genres.keys():
        select = nonempty_genres[g1]
        matches = []
        for g2 in nonempty_genres:
            if g1 == g2:
                matches.append(100.)
            else:
                matches.append(100. * len(select_func(select, g2)) / len(select))
        if rename:
            g1 = rename(g1)
        result[g1] = matches
        genres.append(g1)

    df = pandas.DataFrame(result, index=genres).transpose()
    return df.reindex_axis(sorted(df.columns), axis=1)


def plot_genre_cooccurences_matrix(matrix, figsize=None, title=None):
    plt.figure(figsize=(80, 80))
    seaborn.heatmap(results_cooccurences['genre'], annot=True, fmt='.1f')


    if title is None:
        title = "Genre co-occurrences (%)"

    if PLOT_TITLES:
        plt.title(title)
    else:
        print(title)


def style_cooccurences_by_year(data, style, styles=None, start_year=START_YEAR, end_year=END_YEAR):
    """
    Analyze style co-occurrences by year
    - data: input DataFrame with releases
    - style: the style for which to compute co-occurrences
    - styles: styles to compute co-occurrences with.
              If None, all styles found in data will be used
    """
    if not styles:
        styles = find_styles(data)
    styles = [s for s in styles if s != style]

    stats = {'styles': {}, 'query_style': style}

    for s in styles:
        #print "Analyzing", s, len(styles)
        if s == style:
            continue
        years, releases = releases_per_year(data, start_year, end_year, style=s)
        if 'years' not in stats:
            stats['years'] = years
        stats['styles'][s] = releases

    _, stats['All'] = releases_per_year(data, start_year, end_year)

    return stats


def plot_style_cooccurences_by_year(stats):
    styles = stats['styles'].keys()

    # Plot only styles that have high co-occurrence, at least in some year
    show_styles = [g for g in styles if (100. * stats[g]/stats['All']).max() >= 10]

    #for g in show_styles:
    #    print g, (100. * stats[g]/stats['All']).max()

    for g, c in zip(show_styles, prepare_colors(len(show_styles))):
        tmp = pandas.DataFrame({'All': stats['All'], g: stats[g]})
        plt.plot(stats['years'], 100. * tmp[g] / tmp['All'],
                 label="%s - %s" % (g[0], g[1]),
                 color=c)

    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))

    title = "Percentage of %s releases also annotated by other styles by year (%)" % stats['query_style']
    if PLOT_TITLES:
        plt.title(title)
    else:
        print(title)

    #FIXME hardcoded value that works for ('Electronic', 'House'), but may not work for other styles
    plt.ylim([0, 60])
    plt.show()
    return
