from bs4 import BeautifulSoup
import sqlite3
import re
import os
import getdata
import create_visuals

# inserts each artist's name with their unique Spotify Artist ID into a table in the database
def setIdTable(data):
    try:
        conn = sqlite3.connect('artists_info.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS Artists (artist_id STRING,artist STRING, UNIQUE (artist))')

        for artist in data:
            try:
                cur.execute("INSERT OR IGNORE INTO Artists (artist_id,artist) VALUES (?,?)",(data[artist], artist))
        
            except:
                print("Artist is already in table")
        conn.commit()
    except:
        return

# inserts each artist's name with their respective genre, as indicated by Spotify, into the database
def setGenreTable(genre, data):
    try:
        conn = sqlite3.connect('artists_info.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS Genres (genre STRING,artist STRING, UNIQUE (artist))')
        for artist in data:
            try:
                cur.execute("INSERT OR IGNORE INTO Genres (genre,artist) VALUES (?,?)",(genre,artist))
            except:
                print("Genres already in table")
        conn.commit()
    except:
        return
    
# inserts each artist's name with their number of Instagram followers into the database
def setInstagramTable(data):
    try:
        conn = sqlite3.connect('artists_info.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS Instagram (name STRING,num_followers INTEGER, UNIQUE (name))')
        for artist in data:
            username = getdata.get_insta_username(artist)
            num_followers = getdata.get_num_followers(username)
            if num_followers != -1:
                cur.execute("INSERT INTO Instagram (name,num_followers) VALUES (?,?)",(artist,num_followers))
        conn.commit()
    except:
        print("Artists already in table")

# inserts each artist's name with their number of Monthly Spotify Streams into the database
def setStreamsTable(data):
    try:
        conn = sqlite3.connect('artists_info.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS Streams (name STRING,num_streams INTEGER, UNIQUE (name))')
        for artist in data:
            num_streams = int(getdata.get_monthly_listeners(artist, cur))
            cur.execute("INSERT OR IGNORE INTO Streams (name,num_streams) VALUES (?,?)",(artist,num_streams))
        conn.commit()
    except:
        print("Artists already in table")

# inserts each genre with its respective average number of Instagram followers of the artists in that genre
def setGenreAverages():
    conn = sqlite3.connect("artists_info.db")
    cur = conn.cursor()
    cur.execute("SELECT Genres.genre, Instagram.num_followers FROM Genres INNER JOIN Instagram ON Instagram.name = Genres.artist")
    
    genre_followers = cur.fetchall()

    if len(genre_followers) == 0:
        return 0

    sum = 0
    for entry in genre_followers:
        if entry[0] == genre:
            sum += float(entry[1])
    
    average = int(sum / len(genre_followers))

    try:
        conn = sqlite3.connect('artists_info.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS GenreFollowers (genre STRING,avg_followers INTEGER)')
        cur.execute("INSERT OR IGNORE INTO GenreFollowers (genre,avg_followers) VALUES (?,?)",(genre,average))
        conn.commit()
    except:
        print("Genre already in table")


def setGenreStreams(genres):
    conn = sqlite3.connect("artists_info.db")
    cur = conn.cursor()
    cur.execute("SELECT Genres.genre, Streams.num_streams FROM Genres INNER JOIN Streams ON Streams.name = Genres.artist")
    
    genre_streams = cur.fetchall()

    for genre in genres:
        sum = 0
        for entry in genre_streams:
            if entry[0] == genre:
                sum += float(entry[1])

        try:
            conn = sqlite3.connect('artists_info.db')
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS GenreStreams (genre STRING,total_streams INTEGER)')
            cur.execute("INSERT OR IGNORE INTO GenreStreams (genre,total_streams) VALUES (?,?)",(genre,sum))
            conn.commit()
        except:
            print("Genre already in table")

# prints to a txt file each genre collected and its respective average number of Instagram followers for the artists of that genre
def print_genre_averages_to_file(filename):
    conn = sqlite3.connect("artists_info.db")
    cur = conn.cursor()
    cur.execute("SELECT genre, avg_followers FROM GenreFollowers")
    genre_followers = cur.fetchall()

    f = open(filename, "a")

    for entry in genre_followers:
        f.write(entry[0] + ': ' + str(entry[1]) + ' followers\n')
    f.close()

if __name__ == '__main__':
    
    # ensures .txt file is blank
    f = open("genre_average_followers.txt", "w")
    f.write("")
    f.close()

    # list of typical genres
    genres = ["Christian", "Country", "Dance / Electronic", "Funk", "Hip Hop", "Indie", "Jazz", "K-Pop", "Pop", "R&B", "Rock"]
    
    # asks user which genre they want to get data for
    genre = input('Select one of the following genres by entering its respective number:\n1: Christian\n2: Country\n3: Dance / Electronic\n4: Funk\n5: Hip Hop\n6: Indie\n7: Jazz\n8: K-Pop\n9: Pop\n10: R&B\n11: Rock\n')

    while int(genre) < 1 or int(genre) > 11:
        print("Invaliid option, please select another genre")
        genre = input()

    genre = genres[int(genre) - 1]

    genres_ext = {}
    
    genres_ext["Christian"] = 'inspirational'
    genres_ext["Country"] = 'country'
    genres_ext["Dance / Electronic"] = 'edm_dance'
    genres_ext["Funk"] = 'funk'
    genres_ext["Hip Hop"] = 'hiphop'
    genres_ext["Indie"] = 'indie_alt'
    genres_ext["Jazz"] = 'jazz'
    genres_ext["K-Pop"] = 'kpop'
    genres_ext["Pop"] = 'pop'
    genres_ext["R&B"] = 'rnb'
    genres_ext["Rock"] = 'rock'

    genre_artists = getdata.get_artists_in_genre(genres_ext[genre])

    # gathers all data for artists in specified genre and inserts into database
    setGenreTable(genre,genre_artists)
    setIdTable(genre_artists)
    setStreamsTable(genre_artists)
    setInstagramTable(genre_artists)
    setGenreAverages()
    setGenreStreams(genres)

    # uncomment when all data has been gathered to create final visuals
    #create_visuals.create_visuals()

    # uncomment to print the average number of followers per genre to the specified .txt file
    # print_genre_averages_to_file("genre_average_followers.txt")
    
