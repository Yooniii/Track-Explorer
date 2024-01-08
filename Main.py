import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
import os
import playlist_creator

with open('styles.css') as f:
  st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

client_id = st.secrets["CLIENT_ID"]
client_secret = st.secrets["CLIENT_SECRET"]

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


st.markdown("<h1 style='text-align: center; font-size: 60px'>TrackExplorer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-top: 6px; font-size: 15px'> A web-based API for music lovers. Discover a similar artist, <p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-top: -20px; margin-bottom: 40px; font-size: 15px'>listen to new track recommendations or build a new playlist.  <p>", unsafe_allow_html=True)

search_choices = ['Song/Track', 'Artist']
search_selected = st.sidebar.selectbox("Search By: ", search_choices)

search_keyword = st.text_input(search_selected + " (Keyword Search)")

search_results = []
tracks =[] 
artists =[]

if search_keyword is not None and len(str(search_keyword)) > 0:
  if search_selected == 'Song/Track':
    tracks = sp.search(q='track:'+ search_keyword, type='track', limit=15)
    tracks_list = tracks['tracks']['items']
    if len(tracks_list) > 0:
      for track in tracks_list: 
       # st.write(track['name'] +" - By - " + track['artists'][0]['name'])
        search_results.append(track['name'] +" - By: " + track['artists'][0]['name'])

  else:
    artists = sp.search(q='artist::'+ search_keyword, type='artist', limit=20)
    artists_list = artists['artists']['items']
    if len(artists_list) > 0:
      for artist in artists_list: 
        search_results.append(artist['name'])

selected_track = None
selected_artist = None

if search_selected == 'Song/Track':
  selected_track = st.selectbox("Select the song/track: ", search_results)

elif search_selected == 'Artist':
  selected_artist = st.selectbox("Select the artist: ", search_results)

def get_recommendations(selected_track):
    # Get track URI
    results = sp.search(q=selected_track, type='track')
    track_uri = results['tracks']['items'][0]['uri']

    # Get recommended tracks
    recommendations = sp.recommendations(seed_tracks=[track_uri])['tracks']
    return recommendations

to_add_tracks = []

@st.cache
def add_tracks (track_id):
  to_add_tracks.append(track_id)
  

if selected_track is not None and len(tracks)>0:
  tracks_list = tracks['tracks']['items']
  track_id = None
  if len(tracks_list)>0:
    for track in tracks_list:
      str_temp = track['name'] + " - By: " + track['artists'][0]['name']
      if str_temp == selected_track:
        track_id = track['id']
        track_album = track['album']['name']
        img_album = track['album']['images'][1]['url']
        recommendations = get_recommendations(selected_track)
        
        for track in recommendations:
            cols = st.columns(2)
            cols[0].image(track['album']['images'][0]['url'])
            cols[1].write(track['name'])
            cols[1].write("Artist: " + track['artists'][0]['name'])

            if track['preview_url'] is not None:
              cols[1].audio(track['preview_url'], format='audio/mp3', start_time=0)
            else:
              cols[1].write("No preview available for this track.")

            add_key =  f"add_btn_{track['id']}"
            add_btn = cols[1].button("Add to Playlist", key = add_key)

  if "add_state" not in st.session_state: 
    st.session_state.add_state = False
            
  if add_btn or st.session_state.add_state:
    st.session_state.add_state = True
    add_tracks(track['id'])
    cols[1].write("Added to playlist!")







def get_related_artists(artist_name, artist_uri):
  results = sp.search(q=artist_name, type='artist')
  items = results['artists']['items']
  related_artists = sp.artist_related_artists(artist_uri)['artists']
  return related_artists

if selected_artist is not None and len(artists)>0:
  artist = artists['artists']['items']
  artist_id = None
  artist_uri = None
  if len(artists_list)>0:
    for artist in artists_list:
      if selected_artist == artist['name']:
        artist_uri = artist['uri']
        related_artists = get_related_artists(selected_artist, artist_uri)

        for artist in related_artists:
          cols = st.columns(2)
          artist_id = artist['id']
          cols[0].image(artist['images'][0]['url'])
          with cols[1]:
            st.write(f"**{artist['name']}**")
            st.write(f"**Followers:** {artist['followers']['total']}")
            st.write(f"**Genres:** {', '.join(artist['genres'])}")
            with st.expander(f"**Top Songs:**"):
              top_tracks = sp.artist_top_tracks(artist_id)
              top_tracks = top_tracks['tracks'][:3]
              i = 1
              for track in top_tracks:
                st.write(f"{i}. {track['name']}")
                i+=1

    



        

