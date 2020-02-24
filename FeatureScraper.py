'''
This scripts scrapes the Spotify API for song features from a list of song IDs.
In this case, I'm scraping features from all songs scraped from the Top 200
daily charts on spotifycharts.com.
'''

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import numpy as np
import re


def access_api(client_id, client_secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API
    return sp


def get_features_by_track_list(sp, track_id_list):
    if len(track_id_list) > 100:
        track_id_list = track_id_list[:100]
    track_list = ['spotify:track:{}'.format(track_id) for track_id in track_id_list]
    features = sp.audio_features(track_list)
    return features

def save_csv(df):
    with open('feature_output.csv', 'w', newline='', encoding="utf-8") as f:
        df.to_csv(f, index=False)


def main():
    client_id = # SECRET
    client_secret = # SECRET

    sp = access_api(client_id, client_secret)

    print('Loading DataFrame...')
    top_200 = pd.read_csv('ranking_output.csv')
    track_urls = top_200['URL'].unique().tolist()
    track_ids = [re.search(r"([^\/]+$)", str(url)).group() for url in track_urls]

    idx = 0
    df = pd.DataFrame()

    while idx < len(track_ids):
        track_id_list = track_ids[idx: idx + 100]
        print('Scraping set {} of {}'.format(int(idx / 100 + 1),
                                             len(track_ids) / 100))
        features = get_features_by_track_list(sp, track_id_list)

        corrected_features = []
        for i in range(len(features)):
            if features[i] is None:
                print('No features for track {}'.format(track_ids[idx + i]))
            else:
                corrected_features.append(features[i])

        idx += 100
        time.sleep(np.random.uniform(1, 3))

        df_temp = pd.DataFrame.from_dict(corrected_features)
        df = pd.concat([df, df_temp])

    save_csv(df)


if __name__ == "__main__":
    main()