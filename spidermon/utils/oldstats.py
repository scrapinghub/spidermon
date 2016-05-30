import os
import os.path
import cPickle as pickle

from scrapy.utils.project import data_path

def _path():
    return data_path('oldstats.json')

def load():
    try:
        with open(_path(), 'r') as source:
            try:
                return pickle.load(source)
            except pickle.UnpicklingError:
                return {}
    except IOError:
        return {}

def persist(stats):
        with open(_path(), 'w') as dest:
            pickle.dump(stats, dest)

