from bs4 import BeautifulSoup
import requests
import sqlite3
import seaborn as sns
import re
import os

def get_num_followers(artist):

    url = "https://www.google.com/search?q=instagram+followers+"
    artist = artist.lower()
    url += artist.replace(' ','')
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    results = soup.find_all('div')

    for result in results:
        if 'class' in result.attrs.keys() and result.attrs['class'] == ['kCrYT']:
            end = result.text.find("www.instagram.com ›")
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
  
  
