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
import getdata

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS Genres")
    cur.execute("CREATE TABLE Genres (genre TEXT, artist TEXT)")

    cur.execute("DROP TABLE IF EXISTS Artists")
    cur.execute("CREATE TABLE Artists (artist_id TEXT, artist TEXT)")

    cur.execute("DROP TABLE IF EXISTS Instagram")
    cur.execute("CREATE TABLE Instagram (name TEXT, num_followers TEXT)")

    cur.execute("DROP TABLE IF EXISTS Streams")
    cur.execute("CREATE TABLE Streams (name TEXT, num_streams TEXT)")

    return cur, conn

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

def average_genre_followers(filename, genre, cur):
    cur.execute("SELECT Genres.genre, Instagram.num_followers FROM Genres INNER JOIN Instagram ON Instagram.name = Genres.artist")
    
    genre_followers = cur.fetchall()

    if len(genre_followers) == 0:
        return 0

    sum = 0
    for entry in genre_followers:
        if entry[0] == genre:
            sum += float(entry[1])
    
    average = int(sum / len(genre_followers))

    f = open(filename, "a")

    f.write(genre + ': ' + str(average) + ' followers\n')
    f.close()

    return average

def write_genre_csv(filename, genres, cur, conn):
    with open(filename, 'w') as csvfile:
        write = csv.writer(csvfile, delimiter=',')
        write.writerow(['genre', 'avg_followers'])
        for i in genres:
            write.writerow( (i, genres[i]) )

def write_top_artists_csv(filename, cur, conn):
    with open(filename, 'w') as csvfile:
        write = csv.writer(csvfile, delimiter=',')
        write.writerow(['num_followers','num_streams','name'])
        cur.execute("SELECT Instagram.num_followers, Streams.num_streams, Instagram.name FROM Instagram INNER JOIN Streams ON Streams.name = Instagram.name")
        data = cur.fetchall()
        for i in data:
            write.writerow( (i[0], i[1], i[2]) )
            
 def create_genre_graph():
    sns.set_theme()
    insta = pd.read_csv('genres.csv')
    plot = sns.barplot(
        data=insta,
        x="genre", y="avg_followers",
    )

    for item in plot.get_xticklabels():
        item.set_rotation(45)

    matplotlib.pyplot.show()

def create_top_artists_graph():
    sns.set_theme()
    artists = pd.read_csv('top_artists.csv')
    artists.head()
    plot = sns.scatterplot(
        data=artists,
        x="num_streams", y="num_followers",
    )

    matplotlib.pyplot.show()

if __name__ == '__main__':
    cur, conn = setUpDatabase('artists.db')

    f = open("genre_average_followers.txt", "w")
    f.write("")
    f.close()

    genre_followers = {}

    genres = ["Pop", "Indie", "Hip Hop", "Country", "R&B", "Rock", "Dance / Electronic", "Funk", "K-Pop", "Jazz"]
    
    genres_ext = {}
    genres_ext["Pop"] = 'pop'
    genres_ext["Indie"] = 'indie_alt'
    genres_ext["Hip Hop"] = 'hiphop'
    genres_ext["Country"] = 'country'
    genres_ext["R&B"] = 'rnb'
    genres_ext["Rock"] = 'rock'
    genres_ext["Dance / Electronic"] = 'edm_dance'
    genres_ext["Funk"] = 'funk'
    genres_ext["K-Pop"] = 'kpop'
    genres_ext["Jazz"] = 'jazz'

    for genre in genres:
        genre_artists = getdata.get_artists_in_genre(genres_ext[genre])
        for i in range(0,len(genre_artists) - 2,2):
            curr_artists = {k: genre_artists[k] for k in list(genre_artists)[i:i+2]}
            getdata.gather_data(genre, curr_artists, cur, conn)


        genre_followers[genre] = average_genre_followers("genre_average_followers.txt",genre, cur)

    write_genre_csv("genres.csv", genre_followers, cur, conn)
    write_top_artists_csv("top_artists.csv", cur, conn)

    create_genre_graph()
    create_top_artists_graph()
    
    conn.close() 
