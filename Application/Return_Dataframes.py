#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sqlite3
from sqlite3 import Error

from pyspark.sql import Row
from pyspark.sql import SQLContext
from pyspark import SparkContext
from pyspark.sql.functions import udf
from pyspark.sql.types import (StructField,StructType,StringType,FloatType,IntegerType)

import pandas as pd


# In[2]:


def create_connection(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
 
    return connection


# In[3]:


def return_rows_from_sqlite(select_sql):
    try:
        c = conn.cursor()
        c.execute(select_sql)
        rows = c.fetchall()
        c.close()  
        
        return rows
    except Error as e:
        print(e)


# In[4]:


def return_spark_df(select_sql, data_schema, sampling_ratio = None):
    
    rows = return_rows_from_sqlite(select_sql)
    rdd = sc.parallelize(rows)
    df = sqlContext.createDataFrame(rdd, StructType(fields=data_schema), sampling_ratio)
    
    return df


# In[5]:


def return_sentiment_df():
    data_schema = [StructField('sentiment_id', StringType(), False),
           StructField('user_name', StringType(), False),
           StructField('tweet', StringType(), False),
           StructField('longitude', FloatType(), False),
           StructField('latitude', FloatType(), False),
           StructField('sentiment', StringType(), True)
          ]
    
    select_sql = "select * from sentiment_table where sentiment != ''"
    
    sentiment_df = return_spark_df(select_sql, data_schema)
    sentiment_df_pandas = sentiment_df.toPandas()
    
    return sentiment_df_pandas


# In[6]:


def return_graph_df():
    data_schema = [StructField('graph_id', StringType(), False),
                   
           StructField('id', StringType(), True),
           StructField('text', StringType(), True),
           StructField('screen_name', StringType(), True),
                   
           StructField('user_id', StringType(), True),
           StructField('followers_count', StringType(), True),
           StructField('user_mentions_screen_name', StringType(), True),
                   
           StructField('user_mentions_id', StringType(), True),
           StructField('retweeted_screen_name', StringType(), True),
           StructField('retweeted_id', StringType(), True),
                   
           StructField('in_reply_to_screen_name', StringType(), True),
           StructField('in_reply_to_status_id', StringType(), True),
           StructField('in_reply_to_user_id', StringType(), True)
          ]
    
    select_sql = "select * from graph_table"
    
    graph_df = return_spark_df(select_sql, data_schema, 0.2)
    graph_df_pandas = graph_df.toPandas()
    graph_df_pandas = graph_df_pandas.where((pd.notnull(graph_df_pandas)), None)
    
    return graph_df_pandas


# In[7]:


def return_word_df():
    data_schema = [StructField('word_id', StringType(), False),
                   
           StructField('id', StringType(), True),
           StructField('text', StringType(), True),
           StructField('screen_name', StringType(), True),      
           StructField('user_id', StringType(), True)
          ]
    
    select_sql = "select * from word_table"
    
    word_df = return_spark_df(select_sql, data_schema, 0.2)
    word_df_pandas = word_df.toPandas()
    word_df_pandas = word_df_pandas.where((pd.notnull(word_df_pandas)), None)
    
    return word_df_pandas


# In[8]:


def return_hashtag_df():
    data_schema = [StructField('hashtag_id', StringType(), False),
                  
         StructField('id', StringType(), True),
         StructField('text', StringType(), True),
         StructField('screen_name', StringType(), True),
         StructField('user_id', StringType(), True),
         StructField('hashtags', StringType(), True),
         StructField('polls', StringType(), True),
         StructField('source', StringType(), True),
         StructField('reply_count', StringType(), True),
         StructField('retweet_count', StringType(), True)
        ]
    
    select_sql = "select * from hashtag_table"
    
    hashtag_df = return_spark_df(select_sql, data_schema, 0.2)
    hashtag_df_pandas = hashtag_df.toPandas()
    
    return hashtag_df_pandas


# In[9]:


global conn, sc, sqlContext

database = "Twitter_Database.db"   
conn = create_connection(database)

sc = SparkContext()
sqlContext = SQLContext(sc)


# In[ ]:




