import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
import os

with open('./static/styles.css') as f:
  st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

client_id = st.secrets["CLIENT_ID"]
client_secret = st.secrets["CLIENT_SECRET"]
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

search_results = []
tracks = [] 
artists = []

def display_header():
  st.markdown("<h1 style='text-align: center; font-size: 60px'>TrackExplorer</h1>", unsafe_allow_html=True)
  st.markdown("<p style='text-align: center; margin-top: 6px; font-size: 15px'> A music-recommendation system for music lovers. Discover a similar <p>", unsafe_allow_html=True)
  st.markdown("<p style='text-align: center; margin-top: -20px; margin-bottom: 40px; font-size: 15px'>artist, listen to new track recommendations or build a new playlist.  <p>", unsafe_allow_html=True)

def get_recommendations(selected_track):
  results = sp.search(q=selected_track, type='track')
  track_uri = results['tracks']['items'][0]['uri']
  recommendations = sp.recommendations(seed_tracks=[track_uri])['tracks']
  return recommendations

def get_related_artists(artist_name, artist_uri):
  results = sp.search(q=artist_name, type='artist')
  items = results['artists']['items']
  related_artists = sp.artist_related_artists(artist_uri)['artists']
  return related_artists

def display_audio(track, col):
    if track['preview_url'] is not None:
      col.audio(track['preview_url'], format='audio/mp3', start_time=0)
    else:
      col.write("No preview available for this track.")

def display_tracks(tracks_list, selected_track):
  for track in tracks_list:
    str_temp = track['name'] + " - By: " + track['artists'][0]['name']
    
    if str_temp == selected_track:
      recommendations = get_recommendations(selected_track)
          
      with st.form(f"{track['id']}", clear_on_submit=False, border = False):
        choice_list =[]
        st.write("")
        submitted = st.form_submit_button("Add Selected Songs")

        for track in recommendations:
          cols = st.columns(2)
          cols[0].image(track['album']['images'][0]['url'])
          cols[1].write(f"#### **{track['name']}**")
          cols[1].write(f"**Artist:** " + track['artists'][0]['name'])
          save_key = (f"save_key{track['id']}")          
          save_btn = cols[1].checkbox("Select Song", key={track['id']}, value = False)
          display_audio(track, cols[1])
          
          if save_btn == True:
            choice_list.append(track['name'])
            
          if submitted:
            st.write(choice_list)   

def display_artists(artists_list, selected_artist):
  for artist in artists_list:
    if selected_artist == artist['name']:
      artist_uri = artist['uri']
      related_artists = get_related_artists(selected_artist, artist_uri)

      for artist in related_artists:
        cols = st.columns(2)
        artist_id = artist['id']
        cols[0].image(artist['images'][0]['url'])
          
        with cols[1]:
          st.write(f"#### **{artist['name']}**")
          st.write(f"**Followers:** {artist['followers']['total']}")
          st.write(f"**Genres:** {', '.join(artist['genres'])}")
          
          with st.expander(f"**Top Songs:**"):
            top_tracks = sp.artist_top_tracks(artist_id)
            top_tracks = top_tracks['tracks'][:3]
            i = 1
            for track in top_tracks:
              st.write(f"{i}. {track['name']}")
              i+=1

def main():
  display_header()
  search_choices = ['Song/Track', 'Artist']
  search_selected = st.sidebar.selectbox("Search By: ", search_choices)
  search_keyword = st.text_input(search_selected + " (Keyword Search)")
  selected_track = None
  selected_artist = None

  if search_keyword is not None and len(str(search_keyword)) > 0:
    if search_selected == 'Song/Track':
      tracks = sp.search(q='track:'+ search_keyword, type='track', limit=15)
      tracks_list = tracks['tracks']['items']
      
      if len(tracks_list) > 0:
        for track in tracks_list: 
          search_results.append(track['name'] +" - By: " + track['artists'][0]['name'])
        selected_track = st.selectbox("Select the song/track: ", search_results)
        
        if selected_track is not None and len(tracks) > 0:
          tracks_list = tracks['tracks']['items']
          display_tracks(tracks_list, selected_track)
        
      else:
        st.write("That track does not exist in our database.")


    else:
      artists = sp.search(q='artist::'+ search_keyword, type='artist', limit=20)
      artists_list = artists['artists']['items']
      
      if len(artists_list) > 0:
        for artist in artists_list: 
          search_results.append(artist['name'])
        selected_artist = st.selectbox("Select the artist: ", search_results)
        
        if selected_artist is not None and len(artists) > 0:
          artist = artists['artists']['items']
          display_artists(artists_list, selected_artist)
        
      else:
        st.write("That artist does not exist in our database.")
        
main()