# current25
Fetches your 25 most recent Liked Songs from Spotify into a Spotify playlist.
This playlist is automatically created once and automatically updated every hour.
Hence, you always have a playlist with your current 25 favourite songs which you can shuffle and share.

![](screenshot.JPG)

## 2 Types of Using
You can either use this tool directly via this website: https://current25.mariewetzig.de \
Or, you can run this program on your own server.
Only in the second case the following information is relevant:

### Dependencies
- bottle: Install bottle so that the users' spotify login is handled via web server.\
 ```
  pip3 install bottle
 ```
- spotipy: Install spotipy, a wrapper for the Spotify Web API.\
 ```
  pip3 install spotipy
 ```
  
### Configuration
You need to write a config.py file and save it in your local current25 directory.
The config.py should look like this:
### Run
Now you can run current25.py with python3.
- The playlist "current 25" will be created automatically. You can change its name, privacy, etc.
- The idea is to run current25.py permanently; then your playlist will be updated hourly.
