#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tweepy 
import networkx as nx
from operator import itemgetter
import pandas as pd
import collections
import re

import nltk
from nltk.corpus import stopwords
# nltk.download('stopwords')


# In[2]:


def read_outh_file(outh_filename):
    keys = []
    with open(outh_filename) as fp:
        line = fp.readline()
        while line:
            keys.append(line.strip('\n'))
            line = fp.readline()

    consumer_key = keys[0]
    consumer_secret_key = keys[1]
    access_token = keys[2]
    access_secret_token = keys[3]
    
    return consumer_key,consumer_secret_key,access_token,access_secret_token


# In[3]:


def autorize_twitter_api():

    consumer_key,consumer_secret_key,access_token,access_secret_token = read_outh_file("outh.txt")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_secret_token)
    
    return auth


# In[4]:


def create_network_graph(graph_df):
    
    dff = graph_df.sample(frac=1).tail(1000)

    graph = nx.Graph()

    for index, data in dff.iterrows():
        user = data['user_id']
        graph.add_node(user)
        graph.node[user]["name"] = data['screen_name']
        if data['retweeted_id'] is not None:
            retweet = data['retweeted_id']
            graph.add_edge(user, retweet)
            graph.node[retweet]["name"] = data['retweeted_screen_name']

        elif data['in_reply_to_user_id'] is not None:
            reply_user = data['in_reply_to_user_id']
            graph.add_edge(user, reply_user)
            graph.node[reply_user]["name"] = data['in_reply_to_screen_name']

        elif data['in_reply_to_status_id'] is not None:
            reply_status = data['in_reply_to_status_id']
            graph.add_edge(user, reply_status)
            graph.node[reply_status]["name"] = data['in_reply_to_screen_name']

        elif data['user_mentions_id'] is not None:
            user_mentions = data['user_mentions_id']
            graph.add_edge(user, user_mentions)
            graph.node[user_mentions]["name"] = data['user_mentions_screen_name']

    pos = nx.spring_layout(graph, k=0.05)
    for n, p in pos.items():
        graph.node[n]['pos'] = p
        
    return graph


# In[5]:


def return_top_n_users_page_rank(graph, top_n_users = None):
    
    if top_n_users is None:
        top_n_users = 10
    
    
    pr = nx.pagerank(graph)
    sorted_nodes = sorted([(node, pagerank) for node, pagerank in pr.items()], key=lambda x:pr[x[0]])
    
    ids_of_sorted_nodes = [x[0] for x in sorted_nodes][:top_n_users]

    list_users = []
    for id_sorted in ids_of_sorted_nodes:
        name = graph.node[id_sorted]['name']
        list_users.append(name)
        
    df = pd.DataFrame(list_users, columns=["Top User Ranking"])
    
    return df


# In[6]:


def return_unique_searched_terms(data):
    cleaned_text = [text.split('_', 1)[0] for text in data]
    unique_terms = list(set(cleaned_text))
    unique_terms.sort()
    return unique_terms


# In[7]:


def sentiment_colors(sentiment):
    if sentiment == "Positive":
        return "#00ff00"
    elif sentiment == "Negative":
        return "#ff0000"
    else:
        return '#ffff00'


# In[11]:


def return_word_frequency(data):
    no_url_text = [" ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", text).split()) for text in data]
    cleaned_text = [text.lower().split(' ') for text in no_url_text]
    flattened_list = [item for sublist in cleaned_text for item in sublist]
    
    stop_words = list(set(stopwords.words('english')))
    stop_words.append('rt')
    
    remove_stopwords = [word for word in flattened_list if not word in stop_words]
             
    
    count_unique_words = collections.Counter(remove_stopwords)
    
    return count_unique_words.most_common(15) 


# In[1]:


def return_frequent_source(data):
    clean = re.compile('<.*?>')
    no_url_text = [re.sub(clean, '', text) for text in data]
    count_unique_source = collections.Counter(no_url_text)
    return count_unique_source.most_common(15) 


# In[2]:


def return_frequent_hashtags(data):

    remove_text = ["".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", text)) for text in data]
    remove_null = [item for item in remove_text if len(item) != 0]
    count_hashtags = collections.Counter(remove_null)
    return count_hashtags.most_common(15) 


# In[3]:


def return_frequent_users(data):
    count_unique_users = collections.Counter(data)
    return count_unique_users.most_common(15) 


# In[ ]:




