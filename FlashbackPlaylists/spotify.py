from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os


class PlaylistGenerator:

    def generate_playlist(date, title, description):

        CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
        SECRET = os.environ.get("SPOTIFY_SECRET")
        REDIRECT_URL = "http://example.com"
        OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
        OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

        # connect to Spotify Account
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope="playlist-modify-public",
                redirect_uri=REDIRECT_URL,
                client_id=CLIENT_ID,
                client_secret=SECRET,
                show_dialog=True,
                cache_path=".cache",
                username="timonrieger",
            )
        )

        user_id = sp.current_user()["id"]

        response = requests.get(
            url="https://www.billboard.com/charts/hot-100/" + date + "/")
        website_html = response.text

        soup = BeautifulSoup(website_html, "html.parser")

        song_name = soup.select(selector="ul li ul li h3")
        song_list = [song.getText().strip() for song in song_name]

        year = date.split("-")[0]

        # get the uri for each song and append it to the list song_uris

        song_uris = []
        for song in song_list:
            try:
                uri = sp.search(q=f"track:{song} year:{year}")[
                    "tracks"]["items"][0]["uri"]
                song_uris.append(uri)
            except IndexError:
                pass


        # create private playlist
        create_playlist = sp.user_playlist_create(user=user_id, name=title,
                                                  public=True, description=description)

        # use the playlist id to add the song (uri) to the playlist
        sp.playlist_add_items(playlist_id=create_playlist["id"], items=song_uris)

        # get playlist url
        playlist_url = create_playlist["external_urls"]["spotify"]

        return playlist_url
