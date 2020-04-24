# -*- coding: utf-8 -*-
import requests
import random
import time
import requests_cache
import traceback
from sqlite_functions import SqLite

requests_cache.install_cache(expire_after=3000)


class LastFm:
    def __init__(self, api_key, user_agent, db_name, _format='json'):
        """init for lasfm api client
        {user_agent} for lastf knows wtf we are
        {api_key} for api_key for our app"""
        self.headers = {'user_agent': user_agent}
        self.payload = {'api_key': api_key,
                        'format': _format}
        self.url = 'http://ws.audioscrobbler.com/2.0/'
        self.db = SqLite(db_name)

    def lastfm_get(self, method, limit=500):
        """get requests data
        {method} for method from https://www.last.fm/api/
        {limit} is for count result per page"""
        try:
            self.payload['method'] = method
            self.payload['limit'] = limit
            response = requests.get(self.url, headers=self.headers, params=self.payload)
            if response.status_code == 200 and not getattr(response, 'from_cache', False):
                time.sleep(0.25)
                return response.json()
            elif response.status_code != 200:
                print("i'm not ok")
            else:
                return response.json()
        except Exception as e:
            traceback.print_exc()

    def get_token(self):
        """obtain token for authentication"""
        try:
            return self.lastfm_get('auth.getToken')['token']
        except Exception as e:
            traceback.print_exc()
            return e

    def get_library_page(self, login, page=1, limit=500):
        """obtain one page of user library
        {user} is for that user
        {page} is for wich page to gain
        {limit} is for limit of results per page"""
        self.payload['page'] = page
        try:
            library = self.lastfm_get('library.getArtists', limit=limit)
            if all([library,
                    library['artists'],
                    library['artists']['artist'],
                    int(library['artists']['@attr']['page']) <= int(library['artists']['@attr']['totalPages']),
                    ]):
                return ([{'url': i['url'],
                          'playcount': int(i['playcount']),
                          'artist': i['name'],
                          'id': '{}_{}'.format(login, i['name']),
                          'user': login} for i in library['artists']['artist']])
        except Exception as e:
            traceback.print_exc()

    def get_library(self, login, method, table):
        """obtain full library of some user
        {login} is for that user
        {method} is for what to gain"""
        try:
            """get one page"""
            self.payload['user'] = login
            page = 1
            while True:
                print(page)
                if method == 'library':
                    data = self.get_library_page(login, page)
                elif method == 'recent':
                    data = self.get_recent_track(login, page)
                if data:
                    """insert to local bd"""
                    self.db.insert_table(table_name=table, data=data, if_exist=True)
                    page += 1
                else:
                    break
        except Exception as e:
            traceback.print_exc()

    def get_recent_track(self, login, page=1, limit=500):
        """obtain full scrobbled tracks of some user
        {login} is for that user"""
        self.payload['user'] = login
        self.payload['page'] = page
        try:
            recent = self.lastfm_get('user.getRecentTracks', limit=limit)
            if all([recent,
                    recent.get('recenttracks'),
                    recent.get('recenttracks').get('track'),
                    recent['recenttracks']['@attr'],
                    recent['recenttracks']['track']]):
                tracks = []
                for track in recent['recenttracks']['track']:
                    track_info = self.get_track_info(track['name'], track['artist']['#text'])
                    tracks.append({
                        'url': track['url'],
                        'artist': track['artist']['#text'],
                        'album': track['album']['#text'],
                        'id': '{}_{}_{}_{}'.format(login,
                                                   track['name'],
                                                   track['artist']['#text'],
                                                   track.get('date').get('uts')
                                                   if track.get('date') else random.randint(0, 10000000)),
                        'track':  track['name'],
                        'date': track.get('date').get('uts') if track.get('date') else None,
                        'user': login,
                        'duration': track_info.get('duration') if track_info else None,
                        'listeners': track_info.get('listeners') if track_info else None,
                        'full_playcount': track_info.get('full_playcount') if track_info else None,
                        'toptags': track_info.get('toptags') if track_info else None})
                return tracks
        except Exception as e:
            traceback.print_exc()

    def get_track_info(self, track, artist):
        """obtain info about track
        {track} - name of track
        {artist} - witch artist's track"""
        self.payload['track'] = track
        self.payload['artist'] = artist
        self.payload['autocorrect'] = 1
        try:
            track_info = self.lastfm_get('track.getInfo')
            if all([track_info,
                    track_info.get('track')]):
                return {'name': track_info['track']['name'],
                        'url': track_info['track']['url'],
                        'duration': int(track_info['track']['duration']),
                        'listeners': int(track_info['track']['listeners']),
                        'full_playcount': int(track_info['track']['playcount']),
                        'toptags': ', '.join([i['name'] for i in track_info['track']['toptags']['tag']])
                        if track_info['track']['toptags']['tag'] else ''
                        }
        except Exception as e:
            traceback.print_exc()


