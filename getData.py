from bs4 import BeautifulSoup
import requests
import sqlite3
import seaborn as sns
import re
import os
import csv
import numpy as np
import matplotlib
import pandas as pd

def get_num_followers(artist):

    url = "https://www.google.com/search?q=instagram+followers+"
    artist = artist.lower()
    url += artist.replace(' ','')
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    results = soup.find_all('div')

    for result in results:
        if 'class' in result.attrs.keys() and result.attrs['class'] == ['kCrYT']:
            end = result.text.find("www.instagram.com ")
            if end != -1:
                result = result.next_sibling.next_sibling
                break
    
    end = result.text.find("Followers")
    if end != -1:
        end -= 2
        if result.text[end] >= '0' and result.text[end] <= '9':
            return float(result.text[0:end + 1])
        else:
            num_followers = float(result.text[0:end])
            if result.text[end] == 'm':
                num_followers *= 1000000
            elif result.text[end] == 'k':
                num_followers *= 10000
            return num_followers

    return 0

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

    while result.contents[0].find("artists", start) != -1 and i < 19:
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

def setUpIdTable(data, cur, conn):
    for artist in data:
        cur.execute("INSERT INTO Artists (artist_id,artist) VALUES (?,?)",(data[artist], artist))
    conn.commit()

def setUpGenreTable(genre, data, cur, conn):
    for artist in data:
        cur.execute("INSERT INTO Genres (genre,artist) VALUES (?,?)",(genre,artist))
    conn.commit()

def setUpInstagramTable(data, cur, conn):
    for artist in data:
        num_followers = len(artist)
        #num_followers = get_num_followers(artist)
        cur.execute("INSERT INTO Instagram (name,num_followers) VALUES (?,?)",(artist,num_followers))
    conn.commit()

def setUpStreamsTable(data, cur, conn):
    for artist in data:
        #num_streams = len(artist)
        num_streams = get_monthly_listeners(artist, cur)
        cur.execute("INSERT INTO Streams (name,num_streams) VALUES (?,?)",(artist,num_streams))
    conn.commit()

def gather_data(genre, genre_artists, cur, conn):
    
    setUpGenreTable(genre, genre_artists, cur, conn)
    setUpIdTable(genre_artists, cur, conn)
    setUpInstagramTable(genre_artists, cur, conn)
    setUpStreamsTable(genre_artists, cur, conn)
