# current25
Puts your 25 most recent Liked Songs from Spotify into a Spotify playlist.
This playlist is automatically created once and updated every 5 minutes.
Hence, you always have a playlist with your current 25 favourite songs which you can shuffle and share.

![](screenshot.JPG)

## 2 Types of Using
You can either use this tool directly via this website: https://current25.mariewetzig.de \
Or, you can run this program on your own server.
Only in the second case the following information is relevant:

### Dependencies
- bottle: Install bottle so that the users' spotify login is handled via web server.
 ```
  pip3 install bottle
 ```
- spotipy: Install spotipy, a wrapper for the Spotify Web API.
 ```
  pip3 install spotipy
 ```
  Also, you need to create an app on the Spotify for Developers Site. Here you'll get an ID and key for your app.
### Configuration
You need to write a config.py file and save it in your local current25 directory.
The config.py should look like this:
 ```
MY_ID = <your ID for this Spotify App>
MY_SECRET = <your secret key for this Spotify App>
PORT_NUMBER = <port number of the local website which handles spotify login>
SPOTIFY_REDIRECT_URI = <redirect uri>
CACHE = <cache>
 ```
### Run
Now you can run current25.py with python3.
- The playlist "my current 25" will be created automatically. You can change its name, privacy, etc.
- The idea is to run current25.py permanently; then your playlist will be updated hourly.
