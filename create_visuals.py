import seaborn as sns
import sqlite3
import numpy as np
import matplotlib
import pandas as pd

# creates bar graph using seaborn to display each genre with the average number of Instagram followers of the artists in that genre
def create_genre_graph():
    conn = sqlite3.connect('artists_info.db')
    genre_followers = pd.read_sql_query("SELECT genre, avg_followers FROM GenreFollowers", conn)

    sns.set_theme()
    plot = sns.barplot(
        data=genre_followers,
        x="genre", y="avg_followers",
    )

    for item in plot.get_xticklabels():
        item.set_rotation(45)

    matplotlib.pyplot.show()

# creates a scatterplot using seaborn to display the relationship between number of Monthly Spotify Streams with number of Instagram followers
# for each artist
def create_top_artists_graph():

    conn = sqlite3.connect('artists_info.db')
    stats = pd.read_sql_query("SELECT Instagram.num_followers, Streams.num_streams FROM Instagram INNER JOIN Streams ON Streams.name = Instagram.name", conn)

    sns.scatterplot(
        data=stats,
        x="num_streams", y="num_followers",
    )

    matplotlib.pyplot.show()
    
    def create_streams_graph():
    conn = sqlite3.connect('artists_info.db')
    genre_streams = pd.read_sql_query("SELECT genre, total_streams FROM GenreStreams", conn)

    sns.set_theme()
    plot = sns.barplot(
        data=genre_streams,
        x="genre", y="total_streams",
    )

    for item in plot.get_xticklabels():
        item.set_rotation(45)

    matplotlib.pyplot.show()

def create_visuals():

    create_genre_graph()
    create_top_artists_graph()
    create_streams_graph()

