#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Load Discogs releases dump, parse XML, clean and prepare data.
Store results into a text file dump with each line representing information
about a particular release in a json format.
'''

from gzip import GzipFile
import xmltodict
import json
import urllib
import sys
import os.path
from hurry.filesize import size as filesize

from config import *

processed = 0
errors = 0


def download_progress(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    sys.stdout.write("\r...%d%% (%s)" % (percent, filesize(totalSize)))
    sys.stdout.flush()


def get_release(_, release):

    global errors
    global processed

    # remove unnecessary fields
    if 'images' in release:
        del release['images']
    if 'notes' in release:
        del release['notes']
    if 'companies' in release:
        del release['companies']
    if 'identifiers' in release:
        del release['identifiers']
    if 'videos' in release:
        del release['videos']
    if 'extraartists' in release:
        del release['extraartists']

    # simplify some fields
    try:
        release['genres'] = release['genres']['genre']

        if 'styles' in release:
            release['styles'] = release['styles']['style']
        else:
            release['styles'] = []

        release['artists'] = release['artists']['artist']
        release['tracklist'] = release['tracklist']['track']
        release['formats'] = release['formats']['format']
        release['labels'] = release['labels']['label']

    except:
        print("Error reading", json.dumps(release, indent=4))
        errors += 1
        return True

    if type(release['genres']) is unicode:
        release['genres'] = [release['genres']]

    if type(release['styles']) is unicode:
        release['styles'] = [release['styles']]

    if type(release['artists']) is not list:
        release['artists'] = [release['artists']]

    if type(release['tracklist']) is not list:
        release['tracklist'] = [release['tracklist']]

    if type(release['formats']) is not list:
        release['formats'] = [release['formats']]

    if type(release['labels']) is not list:
        release['labels'] = [release['labels']]

    release['labels'] = list(set([l['@name'] for l in release['labels']]))

    for a in release['artists']:
        del a['anv']
        del a['join']
        del a['role']
        del a['tracks']

    total_duration = 0
    for t in release['tracklist']:
        if 'extraartists' in t:
            del t['extraartists']
        del t['position']
        # del t['title']

        if 'artists' in t:
            t['artists'] = t['artists']['artist']

            if type(t['artists']) is not list:
                t['artists'] = [t['artists']]

            for ta in t['artists']:
                del ta['anv']
                del ta['join']
                del ta['tracks']
                del ta['role']

        # convert duration to seconds
        if t['duration'] is not None:
            try:
                time = [int(x) for x in t['duration'].split(':')]
            except:
                try:
                    time = [int(x) for x in t['duration'].split('.')]
                except:
                    time = []

            if len(time) > 3 or len(time) < 2:
                print("ERROR: unexpected format for duration %s" % t['duration'])
                t['duration'] = None

            if len(time) == 2:
                t['duration'] = time[0] * 60 + time[1]
            elif len(time) == 3:
                t['duration'] = (time[0] * 60 + time[1]) * 60 + time[2]

        if total_duration is not None and t['duration'] is not None:
            total_duration += t['duration']
        else:
            total_duration = None

    release['tracks_number'] = len(release['tracklist'])
    release['tracks_duration'] = total_duration

    # clean format
    for f in release['formats']:
        if '@text' in f:
            del f['@text']

    dump_json_f.write(json.dumps(release)+'\n')

    processed += 1
    if not processed % 10000:
        print("Processed %d releases" % processed)
    return True


if os.path.isfile(dump_gz):
    print("Dump file already found (%s)" % dump_gz)
else:
    print("Downloading Discogs releases data dump archive (%s)" % dump_url)
    urllib.URLopener().retrieve(url, dump_gz, reporthook=download_progress)
    print("")

if os.path.isfile(dump_json):
    print("Json dump file already found (%s)" % dump_json)
else:
    print("Preprocessing data dump archive into json dump (%s)" % dump_json)
    dump_json_f = open(dump_json, 'w')
    xmltodict.parse(GzipFile(dump_gz), item_depth=2, item_callback=get_release)

    print("%d releases loaded" % processed)
    print("%d releases skipped due to errors" % errors)
