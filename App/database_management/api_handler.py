import logging
import matplotlib as mpl

# Local Imports
from flask import current_app
from App.authenticate import (make_get_request, make_post_request, refresh_token)
from App.database_management.db_actions import (db_add_tracks_playlist, db_clear_playlist,
                                                db_get_top_tracks_uri)
from App.database import Session
from App.database_management.user_operations import User

mpl.use('Agg')  # Use MatPlotLib without the GUI


class SpotifyAPIHandler:
    def __init__(self, session):
        self.session = session

    def create_playlist(self, playlist_name):

        """Creates a group of a songs (playlist) with the parameter session and pulls the
                 user inputted playlist name
                 Args:
                    self (Session): Flask Session Object
                    playlist_name (String): Name of the playlist which is being called for

                 Returns:
                     Dictionary: id, uri
                 """
        url = 'https://api.spotify.com/v1/users/' + self.session['user_id'] + '/playlists'
        data = "{\"name\":\"" + playlist_name + "\",\"description\":\"Created by Soulify\",\"public\":false}"
        payload = make_post_request(self.session, url, data)
        current_app.logger.info(f'(createPlaylist) Payload: {payload}')
        if payload is None:
            return None
        return payload['id'], payload['uri']

    @staticmethod
    def update_playlists():
        """Function to literally update playlists. Authorization with spotify is checked. Authorization
        with user is also checked to see if playlist is deleted or not.

        Args:
            No arguments


        Returns:
            No returns. (Checks throughout code for authorization and playlist deleted/updated)
        """
        session = Session()

        # attempt to update each user's playlists
        for user in session.query(User):
            is_active = False

            # authorize the application with Spotify API
            payload = refresh_token(user.refresh_token)

            # if user account has been removed or authorization revoked, user is deleted
            if payload is None:
                session.delete(user)
            else:
                access_token = payload[0]

                playlist = user.playlist_id_short
                if playlist is not None:
                    # if the playlist has not been deleted
                    if db_clear_playlist(access_token, str(playlist)) is not None:
                        uri_list = db_get_top_tracks_uri(access_token, 'short_term', 50)
                        db_add_tracks_playlist(access_token, str(playlist), uri_list)
                        is_active = True
                    else:
                        user.playlist_id_short = None

                playlist = user.playlist_id_medium
                if playlist is not None:
                    if db_clear_playlist(access_token, str(playlist)) is not None:
                        uri_list = db_get_top_tracks_uri(access_token, 'medium_term', 50)
                        db_add_tracks_playlist(access_token, str(playlist), uri_list)
                        is_active = True
                    else:
                        user.playlist_id_medium = None

                playlist = user.playlist_id_long
                if playlist is not None:
                    if db_clear_playlist(access_token, str(playlist)) is not None:
                        uri_list = db_get_top_tracks_uri(access_token, 'long_term', 50)
                        db_add_tracks_playlist(access_token, str(playlist), uri_list)
                        is_active = True
                    else:
                        user.playlist_id_long = None

                # if no playlists could be updated, then remove user
                if not is_active:
                    session.delete(user)

        session.commit()
        session.close()

        logging.info('Updated TopTracks Playlists')

    def add_tracks_playlist(self, playlist_id, uri_list):
        """Using the spotify API to add singular tracks to a playlist.

        Args:
            self (Session): Flask Session Object
            playlist_id (int): ID for the playlist for spotify API to function
            uri_list (): [description] **Will come back to

        Return:
            No return.
        """
        url = 'https://api.spotify.com/v1/playlists/' + str(playlist_id) + '/tracks'

        uri_str = ""
        for uri in uri_list:
            uri_str += "\"" + uri + "\","

        data = "{\"uris\": [" + uri_str[0:-1] + "]}"
        make_post_request(self.session, url, data)

        return

    def get_tracks_playlist(self, playlist_id, limit=100):
        """Get function which uses the spotify API along as the playlist ID in order to get all the
        tracks from the playlist.


        Args:
            self (Session): Flask Session Object
            playlist_id (int): ID for the playlist for spotify API to function
            limit (int, optional): The literal limit of songs per tracks on the playlist. Defaults to 100.

        Returns:
            [type]: Track uri
        """
        url = 'https://api.spotify.com/v1/playlists/' + str(playlist_id) + '/tracks'

        offset = 0
        track_uri = []

        # iterate through all tracks in a playlist (Spotify limits number per request)
        total = 1
        while total > offset:
            params = {'limit': limit, 'fields': 'total,items(track(uri))', 'offset': offset}
            payload = make_get_request(self.session, url, params)

            if payload is None:
                return None

            for item in payload['items']:
                track_uri.append(item['track']['uri'])

            total = payload['total']
            offset += limit

        return track_uri

    def get_all_top_tracks(self, limit=10):
        """Creates a list of tracks which are in the top 10 in the spotify API list.

        Args:
            self (Session): Flask Session Object
            limit (int, optional): Number of songs per top tracks. Defaults to 10. **

        Returns:
            list [String]: Returns the id of the top 10 tracks.
        """
        url = 'https://api.spotify.com/v1/me/top/tracks'
        track_ids = []
        time_range = ['short_term', 'medium_term', 'long_term']

        for time in time_range:
            track_range_ids = []

            params = {'limit': limit, 'time_range': time}
            payload = make_get_request(self.session, url, params)

            if payload is None:
                return None

            for track in payload['items']:
                track_range_ids.append(track['id'])

            track_ids.append(track_range_ids)

        return track_ids

    def get_top_tracks_uri(self, time, limit=25):
        """[summary]

        Args:
            self (Session): Flask Session Object
            time (int): The range of time per song.
            limit (int, optional): [description]. Defaults to 25.

        Returns:

        """
        url = 'https://api.spotify.com/v1/me/top/tracks'
        params = {'limit': limit, 'time_range': time}
        payload = make_get_request(self.session, url, params)

        if payload is None:
            return None

        track_uri = []
        for track in payload['items']:
            track_uri.append(track['uri'])

        return track_uri

    def get_top_tracks_id(self, time, limit=25):
        """Creates a list of tracks which are top 25 on the spotify API list.

        Args:
            self (Session): Flask Session Object
            time (int): The range of time per song.
            limit (int, optional): Number of tracks per playlist. Defaults to 25.

        Returns:
            list [String]: Returns the id of the top 10 tracks.
        """
        url = 'https://api.spotify.com/v1/me/top/tracks'
        params = {'limit': limit, 'time_range': time}
        payload = make_get_request(self, url, params)

        if payload is None:
            return None

        track_ids = []
        for track in payload['items']:
            track_ids.append(track['id'])

        return track_ids

    def get_top_artists(self, time, limit=10):
        """[summary]

        Args:
            self (Session): Flask Session Object
            time (int): The range of time per song.
            limit (int, optional): Gets the top 10 artists onto the list. Defaults to 10. **

        Returns:
            list [String]: Returns the id of the top 10 Artists.
        """
        url = 'https://api.spotify.com/v1/me/top/artists'
        params = {'limit': limit, 'time_range': time}
        payload = make_get_request(self.session, url, params)

        if payload is None:
            return None

        artist_ids = []
        for artist in payload['items']:
            artist_ids.append(artist['id'])

        return artist_ids

    #
    #
    def get_recommended_tracks(self, search, tunable_dict, limit=25):
        """This call pulls the top 25 tracks which are directed to a playlist.

        Args:
            self (Session): Flask Session Object
            search ([type]): [description]
            tunable_dict (dict):
            limit (int, optional): Number of tracks which the call will pull. Defaults to 25.

        Returns:
            int (?): rec_track_uri
        """
        track_ids = ""
        artist_ids = ""
        for item in search:

            # tracks IDs start with a 't:' to identify them
            if item[0:2] == 't:':
                track_ids += item[2:] + ","

            # artist IDs start with an 'a:' to identify them
            if item[0:2] == 'a:':
                artist_ids += item[2:] + ","

        url = 'https://api.spotify.com/v1/recommendations'
        params = {'limit': limit, 'seed_tracks': track_ids[0:-1], 'seed_artists': artist_ids[0:-1]}
        params.update(tunable_dict)
        payload = make_get_request(self.session, url, params)

        if payload is None:
            return None

        rec_track_uri = []

        for track in payload['tracks']:
            rec_track_uri.append(track['uri'])

        return rec_track_uri

    #
    #
    def get_liked_track_ids(self):
        url = 'https://api.spotify.com/v1/me/tracks'
        payload = make_get_request(self.session, url)

        if payload is None:
            return None

        liked_tracks_ids = []
        for track in payload['items']:
            liked_id = track['track'].get('id', None)
            if liked_id:
                current_app.logger.info(f"\n\n Track ID: {liked_id}")
                liked_tracks_ids.append(liked_id)

        return liked_tracks_ids

    #
    #
    def search_spotify(self, search, limit=4):
        """Searches the entire spotify library using the spotify API call

        Args:
            self (Session): Flask Session Object
            search ([type]): [description]
            limit (int, optional): Limit of searches shown in the search bar. Defaults to 4.

        Returns:
            dictionary: JSON Response
        """
        url = 'https://api.spotify.com/v1/search'
        params = {'limit': limit, 'q': search + "*", 'type': 'artist,track'}
        payload = make_get_request(self.session, url, params)

        if payload is None:
            return None

        # response includes both artist and track names
        results = []
        for item in payload['artists']['items']:
            # append 'a:' to artist URIs so artists and tracks can be distinguished
            results.append([item['name'], 'a:' + item['id'], item['popularity']])

        for item in payload['tracks']['items']:

            # track names will include both the name of the track and all artists
            full_name = item['name'] + " - "
            for artist in item['artists']:
                full_name += artist['name'] + ", "

            # append 't:' to track URIs so tracks and artists can be distinguished
            results.append([full_name[0:-2], 't:' + item['id'], item['popularity']])

        # sort them by popularity (the highest first)
        results.sort(key=lambda x: int(x[2]), reverse=True)

        results_json = []
        for item in results:
            results_json.append({'label': item[0], 'value': item[1]})

        return results_json
