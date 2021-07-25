from bottle import route, run, request
import config
import threading
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp_oauth = SpotifyOAuth(client_id=config.MY_ID,
                        client_secret=config.MY_SECRET,
                        redirect_uri=config.SPOTIFY_REDIRECT_URI,
                        scope="user-library-read,playlist-modify-private",
                        cache_path=config.CACHE)

sp = spotipy.Spotify(auth_manager=sp_oauth)

# handle spotify login via web server

@route('/')
def index():
    global sp_oauth

    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code != url:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            access_token = sp_oauth.get_access_token(code, as_dict=False)

    if access_token:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        # create current 25 playlist for user
        current25 = sp.user_playlist_create(sp.me()['id'], "current 25")
        # list of tupels of user id, playlist id, object with access token
        
    else:
        return htmlForLoginButton()

def htmlForLoginButton():
    auth_url = sp_oauth.get_authorize_url()
    htmlLoginButton = f"<a href='{auth_url}'>Login to Spotify</a>"
    return htmlLoginButton

t = threading.Thread(target=run, kwargs={'host': '', 'port': config.PORT_NUMBER})
t.start()

# create current 25 playlist
current25 = sp.user_playlist_create(sp.me()['id'], "current 25")

# read Liked Songs, delete songs in current 25 and add last 25 Liked Songs
#while True:

    #sleep 2 hrs
