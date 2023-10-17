import spotipy
import math
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import matplotlib as mpl
import matplotlib.pyplot as plt

# Local Imports
from flask import current_app

mpl.use('Agg')  # Use MatPlotLib without the GUI


class DataProcessing:
    def __init__(self, track_ids):
        self.track_ids = track_ids

    def liked_track_ids_df(self):
        ccm = SpotifyClientCredentials(current_app.config['CLIENT_ID'], current_app.config['CLIENT_SECRET'])
        sp = spotipy.Spotify(client_credentials_manager=ccm)

        song_meta = {'id': [], 'album': [], 'name': [],
                     'artist': [], 'explicit': [], 'popularity': []}

        for song_id in self.track_ids:
            meta = sp.track(song_id)  # Get songs meta data

            # Song Id
            song_meta['id'].append(song_id)

            # Album Name
            album = meta['album']['name']
            song_meta['album'] += [album]

            # Song Name
            song = meta['name']
            song_meta['name'] += [song]

            # Artist Name
            s = ', '
            artist = s.join([singer_name['name'] for singer_name in meta['artists']])
            song_meta['artist'] += [artist]

            # Explicit
            explicit = meta['explicit']
            song_meta['explicit'].append(explicit)

            # Popularity
            popularity = meta['popularity']
            song_meta['popularity'].append(popularity)

        # song_meta_df = pd.DataFrame.from_dict(song_meta)

        # Check the song feature
        features = sp.audio_features(song_meta['id'])
        features_df = pd.DataFrame.from_dict(features)

        # Convert milliseconds to minutes
        # duration_ms = The duration of the track in milliseconds
        # 1 minute = 60 seconds = 60 * 1000 milliseconds = 60,000 milliseconds
        features_df['duration'] = features_df['duration_ms'] / 60000

        # Combine dataframes to see individual attributes for a given song
        # final_df = song_meta_df.merge(features_df)

        pd.set_option('display.max_columns', 1000)
        current_app.logger.info("\n Features_DF")
        current_app.logger.info(print(features_df))

        return features_df

    @staticmethod
    def normalize_df(features_df: pd.DataFrame) -> pd.DataFrame:
        music_attributes = features_df.filter(['danceability', 'energy', 'loudness',
                                               'speechiness', 'acousticness', 'instrumentalness'
                                                                              'liveness', 'valence', 'tempo',
                                               'duration'],
                                              axis=1)

        current_app.logger.info("\n Music Attributes BEFORE Scaling")
        current_app.logger.info(print(music_attributes))
        min_max_scalar = MinMaxScaler()
        music_attributes.loc[:] = min_max_scalar.fit_transform(music_attributes.loc[:])

        pd.set_option('display.max_columns', 1000)
        current_app.logger.info("\n Music Attributes AFTER Scaling")
        current_app.logger.info(print(music_attributes))
        return music_attributes

    @staticmethod
    def create_radar_chart(music_attributes: pd.DataFrame):
        # Set Plot Attributes
        plt.style.use('dark_background')
        # fig = plt.figure(figsize=(12, 8))
        # ax = fig.add_subplot(111, projection="polar")  # Axes Subplot
        # Convert Column names to a list
        categories = list(music_attributes.columns)
        value = list(music_attributes.mean())
        value += value[:1]

        # Angles for each category
        angles = [n / float(len(categories)) * 2 * math.pi for n in range(len(categories))]
        angles += angles[:1]

        # Plot
        plt.polar(angles, value)
        plt.fill(angles, value, alpha=0.3)
        plt.xticks(angles[:-1], categories, size=15)
        plt.yticks(color='grey', size=15)
        plt.ioff()  # Turn Interactive Mode Off

        # TODO: How can Radar Chart be saved on Heroku?
        # img_dir = os.path.abspath("../Soulify/App/static/")
        # radar_chart_file = os.path.abspath('../Soulify/App/static/images/radar-chart.png')
        # # Check if the png exists, if it does delete it
        # if os.path.isfile(radar_chart_file):
        # 	current_app.logger.info("Deleting existing Radar Chart png...")
        # 	os.remove(radar_chart_file)
        # fig.savefig(img_dir + "/images/radar-chart.png")
