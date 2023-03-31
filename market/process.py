#!/usr/bin/python3

import wikipedia
import requests
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
import random
import numpy as np
from pyvis.network import Network

# FUNCTIONS

def is_valid(url):
    """finding the valid link"""

    if url:
        if url.startswith('/wiki/'): # you don't need `re` to check it
            if not re.compile('/\w+:').search(url):
                return True

    return False

number_of_colors = 8

def get_links(word):

    url = wikipedia.page(word).url

    r = requests.get(url)
    print('url:', r.url)

    soup = BeautifulSoup(r.text, features="html.parser")

    title = soup.find('h1', {'class': 'firstHeading'})

    print('starting website:', r.url)
    print('titled:', title.text)
    print()

    valid_urls = []
    
    counter = 0
    while counter < 51:
        for link in soup.find_all('a'):
            url = link.get('href', '')
            if url not in valid_urls and is_valid(url):
                valid_urls.append(url)
                counter += 1

    #print(valid_urls)

    #for url in valid_urls:        
    #    print(url)

    df = pd.DataFrame(columns=["link1", "link2"])

    prefix = "https://en.wikipedia.org"

    links = []
    for u in valid_urls:
        link = prefix+str(u)
        print(link)
        links += str(link).split(" ")

    df["link2"] = links
    df["link1"] = url
    return df


def summary(word):
    summary = wikipedia.summary(word , sentences = 4, auto_suggest = False)
    links = wikipedia.page(word, auto_suggest = False).links
    print(type(links))
    return (summary, links)

def make_graph(word, links):
    if len(links) > 50:
        links = random.sample(links,50)
    print(links)
    print(type(links))
    g = nx.Graph()
    g.add_node(word)
    for link in links:
        g.add_node(link)
        g.add_edge(word, link)
    get_colors = lambda n: ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(n)]
    colors = get_colors(50)
    nx.draw(g, with_labels = True, bbox=dict(facecolor="white"), node_size=50, font_size=5, edge_color=colors)
    plt.axis("off")
    axis = plt.gca()
    axis.set_xlim([1.2*x for x in axis.get_xlim()])
    axis.set_ylim([1.2*y for y in axis.get_ylim()])
    plt.tight_layout()
    path = os.getcwd()
    nx.spring_layout(g, k=0.8, iterations=20)
    nt = Network(height='600px', width='100%',  bgcolor="black", font_color="white")
    nt.from_nx(g)
    nt.show("market/static/graph.html")