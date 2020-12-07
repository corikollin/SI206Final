from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import re
import os

# returns a list of 10 of the top artists in the given genre
def get_artists_in_genre(genre):
    url = "https://open.spotify.com"
    genre_url = url + '/genre/' + genre
    r = requests.get(genre_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    results = soup.find_all('a')

    for result in results:
        if 'class' in result.attrs.keys() and result.attrs['class'] == ['cover', 'entity-type-playlist']:
            r = requests.get(url + result.attrs['href'])
            soup = BeautifulSoup(r.text, 'html.parser')
            break

    results = soup.find_all('script')

    for result in results:
        if result.contents != None and len(result.contents) > 0 and result.contents[0][:12] == '\n\t\t\t\tSpotify':
            break
    
    start = 0

    artists = {}
    i = 0

    while result.contents[0].find("artists", start) != -1 and len(artists) < 10:
        start = result.contents[0].find("artists", start)
        id_start = result.contents[0].find("id", start) + 5
        id_end = result.contents[0].find(",", id_start) - 1
        artist_id = result.contents[0][id_start:id_end]

        name_start = result.contents[0].find("name", id_end) + 7
        name_end = result.contents[0].find(",", name_start) - 1
        artist_name = result.contents[0][name_start:name_end]

        start = name_end
        artists[artist_name] = artist_id
        i += 1

    return artists

# searches Google to find a given artist's Instagram username and returns this string
def get_insta_username(artist):
    url = "https://www.google.com/search?q=instagram+username+"
    artist = artist.lower()
    url += artist.replace(' ','+')
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    results = soup.find_all('div')
    username = ''

    for result in results:
        if result.attrs == {} and result.text.find("Instagram photos") != -1:
            start = result.text.find("@")
            end = result.text.find(")",start)
            if end == -1:
                end = result.text.find("Instagram photos") - 3
            username = result.text[start+1:end]
            break
    
    if username == '':
        url = "https://www.google.com/search?q=instagram+"
        artist = artist.lower()
        url += artist.replace(' ','')
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        results = soup.find_all('div')

        for result in results:
            if result.attrs == {} and result.text.find("Instagram photos") != -1:
                start = result.text.find("@")
                end = result.text.find(")",start)
                if end == -1:
                    end = result.text.find("Instagram photos") - 3
                return result.text[start+1:end]
    else:
        return username

    return ''

# returns the number of Instagram followers based on the username given
def get_num_followers(user):

    base_url = "https://www.instagram.com/"
    insta_username = user
    ext = "/?__a=1"

    url = base_url + insta_username + ext

    try:
        response = requests.get(url)
        text = response.text
        data = json.loads(text)

        followers = data['graphql']['user']['edge_followed_by']['count']
        
        return followers
    except:
        return -1

# returns the number of Monthly Spotify Streams of a given artist
def get_monthly_listeners(artist, cur):

    cur.execute("SELECT artist, artist_id FROM Artists")
    artists = cur.fetchall()

    ext = ''
    for current_artist in artists:
        if current_artist[0] == artist:
            ext = current_artist[1]
            break

    url = "https://open.spotify.com/artist/"
    url += ext
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    results = soup.find_all('meta')
    monthly_listeners = 0

    for result in results:
        if result.get('name') != None and result.get('name') == 'description':
            start = result.attrs['content'].find("Monthly Listeners: ")
            end = result.attrs['content'].find("Where People Listen: ", start)
            monthly_listeners = result.attrs['content'][start + 19: end - 2]
            break

    return monthly_listeners
