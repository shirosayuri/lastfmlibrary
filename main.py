# -*- coding: utf-8 -*-
from functions import *
from lasfm_functions import LastFm
from sqlite_functions import SqLite
import pandas as pd
from datetime import datetime

secrets = get_secrets(path)

mySqLite = SqLite(db_name)

mySqLite.create_table('tracks', {'url': 'text',
                                 'artist': 'text',
                                 'album': 'text',
                                 'id': 'text',
                                 'track':  'text',
                                 'date': 'integer',
                                 'user': 'text',
                                 'duration': 'integer',
                                 'listeners': 'integer',
                                 'full_playcount': 'integer',
                                 'toptags': 'text'
                                 },
                      if_exist=True,
                      primary_key='id')

myLastFm = LastFm(api_key=secrets['API_KEY'], user_agent=secrets['USER_AGENT'], db_name=secrets['db_name'])
myLastFm.get_library(secrets['login'], method='recent', table='tracks')

# prepare data for visualisation


def timestamp_to_date(stuff):
    # convert date from unix timestamp
    return datetime.fromtimestamp(stuff).strftime("%d.%m.%Y")


data = pd.DataFrame(mySqLite.select_data('tracks', columns=['track', 'date', 'toptags']))
data.dropna(inplace=True)
# split tracks to multiply rows by tag in toptags
data['toptags'] = data["toptags"].str.split(",", expand=True)

data['date'] = data.apply(lambda row: timestamp_to_date(row['date']), axis=1)
# deleting all stuff without correct date
data = data.drop(data[data['date'] == '01.01.1970'].index)
data = data.groupby(['toptags', 'date']).count()
data.to_csv('tags.csv', ';')

data = pd.DataFrame(mySqLite.select_data('tracks',
                                         columns=['track', 'date', 'album', 'artist', 'url', 'duration', 'id']))
data.dropna(inplace=True)
data['date'] = data.apply(lambda row: timestamp_to_date(row['date']), axis=1)
data = data.drop(data[data['date'] == '01.01.1970'].index)
data = data.groupby(['track', 'date', 'album', 'artist', 'url', 'duration']).count()
data.to_csv('tracks.csv', ';')

