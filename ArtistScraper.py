'''
This script scrapes the Spotify API for all songs by all artists in a given
list. In this case, I'm scraping for all songs by all artists listed on the
Wikipedia page for List of most-streamed artists on Spotify
(https://en.wikipedia.org/wiki/List_of_most-streamed_artists_on_Spotify) in both
most monthly listeners and most followed (as listed on February 21, 2020).
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

def get_albums_by_artist(sp, artist_uri):
    #Pull all of the artist's albums
    sp_albums = sp.artist_albums(artist_uri)
    #Store artist's albums' names' and uris in separate lists
    album_names = []
    album_uris = []
    for i in range(len(sp_albums['items'])):
        album_names.append(sp_albums['items'][i]['name'])
        album_uris.append(sp_albums['items'][i]['uri'])
    
    return album_names, album_uris


def get_features_for_artist(sp, artist):
    result = sp.search(artist, type='artist') #search query
    artist_uri = result['artists']['items'][0]['uri']
    album_names, album_uris = get_albums_by_artist(sp, artist_uri)

    spotify_albums = {}
    album_count = 0
    for uri in album_uris:  # each album
        spotify_albums = album_songs(sp, uri, spotify_albums, artist, album_names, album_count)
        print("Processed " + str(album_names[album_count]))
        album_count += 1

    sleep_min = 2
    sleep_max = 5
    start_time = time.time()
    request_count = 0
    for album in spotify_albums:
        spotify_albums = audio_features(sp, album, spotify_albums)
        request_count += 1
        if request_count % 5 == 0:
            print(str(request_count) + " ablums completed")
            time.sleep(np.random.uniform(sleep_min, sleep_max))
            print('Loop #: {}'.format(request_count))
            print('Elapsed Time: {} seconds'.format(time.time() - start_time))
    return spotify_albums


def feature_df(spotify_albums):
    dic_df = {}
    dic_df['album'] = []
    dic_df['artist'] = []
    dic_df['track_number'] = []
    dic_df['id'] = []
    dic_df['name'] = []
    dic_df['uri'] = []
    dic_df['acousticness'] = []
    dic_df['danceability'] = []
    dic_df['energy'] = []
    dic_df['instrumentalness'] = []
    dic_df['liveness'] = []
    dic_df['loudness'] = []
    dic_df['speechiness'] = []
    dic_df['tempo'] = []
    dic_df['valence'] = []
    dic_df['popularity'] = []
    for album in spotify_albums: 
        for feature in spotify_albums[album]:
            dic_df[feature].extend(spotify_albums[album][feature])
    df = pd.DataFrame.from_dict(dic_df)
    df = df.sort_values('popularity', ascending=False).drop_duplicates('name').sort_index()
    return df


def album_songs(sp, uri, spotify_albums, artist, album_names, album_count):
    album = uri  # assign album uri to a_name
    spotify_albums[album] = {}  # Creates dictionary for that specific album
    # Create keys-values of empty lists inside nested dictionary for album
    spotify_albums[album]['album'] = []  # create empty list
    spotify_albums[album]['artist'] = []
    spotify_albums[album]['track_number'] = []
    spotify_albums[album]['id'] = []
    spotify_albums[album]['name'] = []
    spotify_albums[album]['uri'] = []
    tracks = sp.album_tracks(album)  # pull data on album tracks
    for n in range(len(tracks['items'])): #for each song track
        spotify_albums[album]['album'].append(album_names[album_count])  # append album name tracked via album_count
        spotify_albums[album]['artist'].append(artist)
        spotify_albums[album]['track_number'].append(tracks['items'][n]['track_number'])
        spotify_albums[album]['id'].append(tracks['items'][n]['id'])
        spotify_albums[album]['name'].append(tracks['items'][n]['name'])
        spotify_albums[album]['uri'].append(tracks['items'][n]['uri'])
    return spotify_albums


def audio_features(sp, album, spotify_albums):
    # Add new key-values to store audio features
    spotify_albums[album]['acousticness'] = []
    spotify_albums[album]['danceability'] = []
    spotify_albums[album]['energy'] = []
    spotify_albums[album]['instrumentalness'] = []
    spotify_albums[album]['liveness'] = []
    spotify_albums[album]['loudness'] = []
    spotify_albums[album]['speechiness'] = []
    spotify_albums[album]['tempo'] = []
    spotify_albums[album]['valence'] = []
    spotify_albums[album]['popularity'] = []
    # create a track counter
    track_count = 0
    for track in spotify_albums[album]['uri']:
        # pull audio features per track
        features = sp.audio_features(track)
        
        # Append to relevant key-value
        spotify_albums[album]['acousticness'].append(features[0]['acousticness'])
        spotify_albums[album]['danceability'].append(features[0]['danceability'])
        spotify_albums[album]['energy'].append(features[0]['energy'])
        spotify_albums[album]['instrumentalness'].append(features[0]['instrumentalness'])
        spotify_albums[album]['liveness'].append(features[0]['liveness'])
        spotify_albums[album]['loudness'].append(features[0]['loudness'])
        spotify_albums[album]['speechiness'].append(features[0]['speechiness'])
        spotify_albums[album]['tempo'].append(features[0]['tempo'])
        spotify_albums[album]['valence'].append(features[0]['valence'])
        # popularity is stored elsewhere
        pop = sp.track(track)
        spotify_albums[album]['popularity'].append(pop['popularity'])
        track_count+=1
    return spotify_albums


def save_csv(df):
    with open('artist_output.csv', 'w', newline='', encoding="utf-8") as f:
        df.to_csv(f, index=False)


def main():
    client_id = # SECRET
    client_secret = # SECRET

    sp = access_api(client_id, client_secret)

    top_listened = pd.read_csv('top_monthly_listeners_feb_2020.csv')
    top_followed = pd.read_csv('most_followed_feb_2020.csv')

    top_artists = top_listened['Artist'].tolist()
    top_artists.extend(top_followed['Artist'].tolist())
    top_artists = list(set(top_artists))

    idx = 0
    df = pd.DataFrame()

    for artist in top_artists:
        spotify_albums = get_features_for_artist(sp, artist)

        df_temp = feature_df(spotify_albums)
        df = pd.concat([df, df_temp])

    save_csv(df)


if __name__ == "__main__":
    main()