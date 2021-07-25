from bottle import route, run, request
import config
import pickle
import threading
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp_oauth = SpotifyOAuth(client_id=config.MY_ID,
                        client_secret=config.MY_SECRET,
                        redirect_uri=config.SPOTIFY_REDIRECT_URI,
                        scope="user-library-read,playlist-modify-private,playlist-modify-public",
                        cache_path=config.CACHE)

sp = spotipy.Spotify(auth_manager=sp_oauth)
try:
    with open("user_data", "rb") as f:
        user_data = pickle.load(f)
except:
    user_data=[]

# handle spotify login via web server

@route('/')
def index():
    global sp_oauth

    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        return
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code != url:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            access_token = sp_oauth.get_access_token(code, as_dict=False)

    if access_token:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        user_id = sp.me()['id']
        # create current 25 playlist for user
        current25 = sp.user_playlist_create(user_id, "current 25")["id"]
        # list of tupels of user id, playlist id, object with access token
        user_data.append((user_id, current25, sp))
        with open("user_data", "wb") as f:
            pickle.dump(user_data, f)
        update_user_current25(current25, sp)
    else:
        return htmlForLoginButton()

def htmlForLoginButton():
    auth_url = sp_oauth.get_authorize_url()
    htmlLoginButton = f"<a href='{auth_url}'>Login to Spotify</a>"
    return htmlLoginButton

t = threading.Thread(target=run, kwargs={'host': '', 'port': config.PORT_NUMBER})
t.start()

def update_user_current25(current25, sp):
    items = sp.current_user_saved_tracks(limit=25, offset=0)["items"]
    current_favs = [x["track"]["id"] for x in items]
    sp.playlist_replace_items(current25, current_favs)

# read Liked Songs, delete songs in current 25 and add last 25 Liked Songs
while True:
    for (_, current25, sp) in user_data:
        update_user_current25(current25, sp)
    time.sleep(3600)
