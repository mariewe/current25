from bottle import route, run, request
import config
import pickle
import threading
import time
import string
import random
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp_oauth_global = SpotifyOAuth(client_id=config.MY_ID,
                        client_secret=config.MY_SECRET,
                        redirect_uri=config.SPOTIFY_REDIRECT_URI,
                        scope="user-library-read,playlist-modify-private,playlist-modify-public",
                        cache_path=config.CACHE)

sp = spotipy.Spotify(auth_manager=sp_oauth_global)
try:
    with open("user_data", "rb") as f:
        user_data = pickle.load(f)
except:
    user_data={}

# handle spotify login via web server

@route('/')
def index():

    url = request.url
    code = sp_oauth_global.parse_response_code(url)

    # login button to Spotify API
    if code == url:
        return htmlForLoginButton()

    # in case you're logged in in Spotify API create new cache with token
    print("Found Spotify auth code in Request URL! Trying to get valid access token...")
    cache_file = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    sp_oauth = SpotifyOAuth(client_id=config.MY_ID,
                        client_secret=config.MY_SECRET,
                        redirect_uri=config.SPOTIFY_REDIRECT_URI,
                        scope="user-library-read,playlist-modify-private,playlist-modify-public",
                        cache_path=cache_file)
    sp_oauth.get_access_token(code, as_dict=False)
    token_info = sp_oauth.get_cached_token()
    os.remove(cache_file)

    print("Access token available! Trying to get user information...")
    sp = spotipy.Spotify(token_info['access_token'])
    user_id = sp.me()['id']
    # check if user id already exists in user_data (aka check if playlist exists)
    if user_id in user_data:
        return
    # create current 25 playlist for user
    current25 = sp.user_playlist_create(user_id, "my current 25")["id"]
    # assign user id to of playlist id and token info
    user_data[user_id] = (current25, token_info)
    # write user_data to file
    with open("user_data", "wb") as f:
        pickle.dump(user_data, f)
    # fill the newly created current 25 playlist
    update_user_current25(current25, sp)

def htmlForLoginButton():
    auth_url = sp_oauth_global.get_authorize_url()
    htmlLoginButton = f"<a href='{auth_url}'>Login to Spotify</a>"
    return htmlLoginButton

def update_user_current25(current25, sp):
    items = sp.current_user_saved_tracks(limit=25, offset=0)["items"]
    current_favs = [x["track"]["id"] for x in items]
    sp.playlist_replace_items(current25, current_favs)

def main():
    t = threading.Thread(target=run, kwargs={'host': '', 'port': config.PORT_NUMBER})
    t.start()
    # read Liked Songs, delete songs in current 25 and add last 25 Liked Songs
    while True:
        for (user_id, (current25, token_info)) in user_data.items():
            # refresh access token
            token_info = sp_oauth_global.validate_token(token_info)
            sp = spotipy.Spotify(token_info['access_token'])
            user_data[user_id] = (current25, token_info)
            # update current 25 playlist
            update_user_current25(current25, sp)
        time.sleep(3600)

if __name__ == "__main__":
    main()
