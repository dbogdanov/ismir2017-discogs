#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Load json text dump with releases information into a pandas DataFrame
'''
from config import *
import pandas
import os.path
import json


# Helper functions for loading/preprocessing data


def extract_year(string):
    # extract year from "released" field string
    try:
        year = int(string.split('-')[0])
    except:
        return None
    return year


def extract_style(styles, genres):
    # find a parent genre among genres for each style in styles
    return [(g, s) for s in styles for g in genres if s in GENRE_TREE[g]]


def extract_formats(formats):
    return [f['@name'] for f in formats]


def extract_compilations(formats):
    # processing as a string because parsing dict did not work out due to some unicode errors
    return 'Compilation' in str(formats)


def extract_mixed(formats):
    # processing as a string because parsing dict did not work out due to some unicode errors
    formats = str(formats)
    return "'Mixed'" in str(formats) or "'Partially Mixed'" in str(formats)


def extract_unofficial(formats):
    # processing as a string because parsing dict did not work out due to some unicode errors
    return 'Unofficial Release' in str(formats)


def extract_artists(artists):
    return [a['id'] for a in artists]


def load_releases(size=None, part=100, ignore_genres=None):
    """
    Load 'size' first releases from the json dump (load all releases if None).
    Use the 'part' parameter to specify a percentage of releases to load. For
    example, part=20% will load every 5th release by order of their occurence
    in the dump.

    By default, all releases will be loaded (size=None and part=100).
    """
    data = []
    with open(dump_json, 'r') as f:
        i = 0
        for jsonline in f:

            # load only a percentage of the dataset selecting every Nth release
            if not i % (100/part):

                release = json.loads(jsonline)

                # remove some columns that we won't use to save memory
                del release['data_quality']
                del release['title']
                del release['labels']
                if 'master_id' in release:
                    del release['master_id']

                # if all tracks are annotated by duration ('tracks_duration' is present) then extract them
                if release['tracks_duration'] is not None:
                    for t in release['tracklist']:
                        release.setdefault('tracks_duration_list', [])
                        release['tracks_duration_list'].append(t['duration']/60.)

                # we don't need anything else from tracklist
                del release['tracklist']

                # convert "released" field to float (can't use integer because we need NaN support)
                if 'released' in release:
                    release['released'] = extract_year(release['released'])

                # find parent genres for styles following Discogs genre tree
                if 'styles' in release:
                    release['styles'] = extract_style(release['styles'], release['genres'])

                # cleanup "format" field
                release['compilation'] = extract_compilations(release['formats'])
                release['mixed'] = extract_mixed(release['formats'])
                release['unofficial'] = extract_unofficial(release['formats'])
                release['formats'] = extract_formats(release['formats'])

                # cleanup "artist" field
                release['artists'] = extract_artists(release['artists'])

                data.append(release)

            i += 1
            if not i % 500000:
                print("Processed %d releases" % i)
            if i == size:
                break
    if data == []:
        print("Error loading %s file" % dump_json)
        return None

    data = pandas.DataFrame(data)

    # convert tracks_duration from seconds to minutes
    data['tracks_duration'] = data['tracks_duration'] / 60.

    # TODO: cleanup artist names, keep only ids

    # remove releases by genres from ignore list
    if ignore_genres:
        for g in ignore_genres:
            data = data[data['genres'].apply(lambda x: g not in x)]

    return data


if os.path.isfile(dump_pandas):
    print("Pandas dump file already found (%s)" % dump_pandas)
else:
    print("Loading json dump into a pandas DataFrame")
    data = load_releases(ignore_genres=IGNORE_GENRES, part=100)
    print("Saving DataFrame to %s" % dump_pandas)
    data.to_hdf(dump_pandas, 'w')
