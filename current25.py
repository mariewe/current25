from bottle import route, run, request, template, redirect
import config
import pickle
import threading
import time
import string
import random
import os
import free_ipod_pic
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp_oauth_global = SpotifyOAuth(client_id=config.MY_ID,
                        client_secret=config.MY_SECRET,
                        redirect_uri=config.SPOTIFY_REDIRECT_URI,
                        scope="user-library-read,playlist-modify-private,playlist-modify-public,ugc-image-upload",
                        cache_path=config.CACHE)

try:
    with open("user_data", "rb") as f:
        user_data = pickle.load(f)
except:
    user_data={}

# handle spotify login via web server

@route("/")
def index():
    url = request.url
    code = sp_oauth_global.parse_response_code(url)

    # login page to Spotify API
    if code == url:
        return htmlForLoginPage()

    # in case you're logged in in Spotify API create new cache with token
    print("Found Spotify auth code in Request URL! Trying to get valid access token...")
    cache_file = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    sp_oauth = SpotifyOAuth(client_id=config.MY_ID,
                        client_secret=config.MY_SECRET,
                        redirect_uri=config.SPOTIFY_REDIRECT_URI,
                        scope="user-library-read,playlist-modify-private,playlist-modify-public,ugc-image-upload",
                        cache_path=cache_file)
    try:
        sp_oauth.get_access_token(code, as_dict=False)
    except:
        redirect("https://current25.mariewetzig.de")

    token_info = sp_oauth.get_cached_token()
    os.remove(cache_file)

    print("Access token available! Trying to get user information...")
    sp = spotipy.Spotify(token_info["access_token"])
    user_id = sp.me()["id"]

    # check if user id already exists in user_data and check if playlist exists
    if user_id in user_data and playlist_exists_for_user(user_id, sp):
        return template("ready")

    # create current 25 playlist for user, save playlist id
    current25 = sp.user_playlist_create(user_id, "my current 25", description = "My 25 most recently Liked Songs, \
automatically synced every hour. https://github.com/mariewe/current25")["id"]
    sp.playlist_upload_cover_image(current25, free_ipod_pic.PIC)
    # assign user id to playlist id and token info
    user_data[user_id] = (current25, token_info)
    # write user_data to file
    with open("user_data", "wb") as f:
        pickle.dump(user_data, f)
    # fill the newly created current 25 playlist
    update_user_current25(current25, sp)

    return template("ready")

def htmlForLoginPage():
    auth_url = sp_oauth_global.get_authorize_url()
    return template("login", link=auth_url)

def playlist_exists_for_user(user_id, sp):
    offset = 0
    current25 = user_data[user_id][0]
    while True:
        results = sp.current_user_playlists(offset=offset)
        playlists = results["items"]
        playlist_ids = [item["id"] for item in playlists]
        if current25 in playlist_ids:
            return True
        if len(playlists) < 50 or offset >= 500:
            return False
        offset += 50

def update_user_current25(current25, sp):
    items = sp.current_user_saved_tracks(limit=25, offset=0)["items"]
    current_favs = [x["track"]["id"] for x in items]
    sp.playlist_replace_items(current25, current_favs)

@route("/imprint")
def imprint():
    return template("imprint")

def main():
    t = threading.Thread(target=run, kwargs={"host": "", "port": config.PORT_NUMBER})
    t.start()
    while True:
        users_to_remove = []
        for (user_id, (current25, token_info)) in user_data.items():
            # refresh access token
            try:
                token_info = sp_oauth_global.validate_token(token_info)
            except:
                print("Fehler bei Tokenvalidierung", traceback.format_exc())
                continue
            if token_info is None:
                print("Refresh token didn't work for this user:", user_id)
                continue
            sp = spotipy.Spotify(token_info["access_token"])
            user_data[user_id] = (current25, token_info)
            # remember user if current25 playlist doesn't exist
            if not playlist_exists_for_user(user_id, sp):
                users_to_remove.append(user_id)
                continue
            # update current 25 playlist
            update_user_current25(current25, sp)
        # delete users if their current25 playlist doesn't exist
        for user_id in users_to_remove:
            user_data.pop(user_id)
        time.sleep(3600)

if __name__ == "__main__":
    main()
