# Inspired by "The Come Up" on Youtube, where she created 
# a playlist from her liked songs on Youtube.

# Here, the user enters a sentence, and spotify creates a playlist 
# such that the first word of every song in the playlist when read from
# top to bottom will be the sentence they've chosen.

import json
import requests
import sys
from secrets import spotify_token, spotify_user_id
from exception import ResponseException

class CreatePlaylist:
    
    def __init__(self):
        self.all_song_info = {}
        self.song_names = self.input_list_of_songs()
        
    def create_playlist(self):
        request_body = json.dumps({
            "name" : "Your Sentence Playlist",
            "description" : "There, you've said it through songs!",
            "public" : True
        })
        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            spotify_user_id)
        response = requests.post(
            query,
            data = request_body,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
            )
        response_json = response.json()
        sys.stderr.write(json.dumps(response_json))

        return response_json["id"]
        
        
    def get_spotify_uri(self, song_name):
        query = "https://api.spotify.com/v1/search?query={}&type=track&offset=0&limit=5".format(
            song_name
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]

        # only use the first song
        uri = songs[0]["uri"]

        return uri

    def get_songs_from_list(self, song_names):
        for item in song_names:
            self.all_song_info[item] = {
                "song_name" : item,
                "spotify_uri" : self.get_spotify_uri(item)
            }

    def input_list_of_songs(self):
        sys.stderr.write("Enter songs spaced with commas: ")
        string_names = input()
        return string_names.split(", ")



    def add_song_to_playlist(self):
        """Add all liked songs into a new Spotify playlist"""
        # populate dictionary with our liked songs
        self.get_songs_from_list(self.song_names)

        # collect all of uri
        uris = [info["spotify_uri"]
                for song, info in self.all_song_info.items()]

        # create a new playlist
        playlist_id = self.create_playlist()

        # add all songs into new playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)

        response_json = response.json()
        return response_json

if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.add_song_to_playlist()
