#!/usr/bin/env python
# coding: utf-8

# In[4]:


# import Return_Dataframes as rd


# In[5]:


import Functions as fn


# In[6]:


import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go


# In[7]:


import pandas as pd
pd.set_option('mode.chained_assignment', None)


# ### Dashboard Initialization

# In[8]:


colors = {"background": "#111111", "text": "#A4B2AB", "plot" : "#45464A", "main_background" : "#111111"}
tab_style = {'borderBottom': '1px solid #d6d6d6','padding': '6px'}
tab_selected_style = {'borderTop': '1px solid #d6d6d6','borderBottom': '1px solid #d6d6d6','padding': '6px','fontWeight': 'bold'}


# ### Load Data

# In[ ]:


sentiment_data_on_load = pd.read_csv("sentiment.csv")
unique_sentiment_search_terms = fn.return_unique_searched_terms(sentiment_data_on_load['sentiment_id'])


# In[ ]:


graph_data_on_load = pd.read_csv("graph.csv")
unique_graph_search_terms = fn.return_unique_searched_terms(graph_data_on_load['graph_id'])


# In[ ]:


word_data_on_load = pd.read_csv("word.csv")
unique_word_search_terms = fn.return_unique_searched_terms(word_data_on_load['word_id'])


# In[ ]:


hashtag_data_on_load = pd.read_csv("hashtag.csv", lineterminator='\n')
unique_hashtag_search_terms = fn.return_unique_searched_terms(hashtag_data_on_load['hashtag_id'])


# ### Graphs

# In[ ]:


def create_sentiment_map(sentiment_df, unique_sentiment_search_terms, sentiment_term):
    
    if sentiment_term is None:
        sentiment_term = [unique_sentiment_search_terms[0]]
    
    sentiment_df['search_term'] = sentiment_df.apply (lambda row: row['sentiment_id'].split('_', 1)[0], axis=1)
    
    dff = sentiment_df[sentiment_df['search_term'].isin(sentiment_term)]
    
    dff['colour'] = dff.apply(lambda row: fn.sentiment_colors(row['sentiment']), axis=1)
    
    dff['text'] = 'User: ' + dff['user_name'] + '<br>Tweet: ' + dff['tweet'] + '<br>Sentiment: ' + dff['sentiment']
    
    sentiment_title = [i.title() for i in sentiment_term]
    sentiment_title_join = ", ".join(sentiment_title)
    
    return {
        'data': [go.Scattergeo(
            lon=dff['longitude'],
            lat=dff['latitude'],
            mode='markers',
            marker_color = dff['colour'],
            text= dff['text']
        )],
    
        'layout': 
        go.Layout(
            title= str('Sentiment Analysis for ' + sentiment_title_join),
            plot_bgcolor = colors['plot'],
            paper_bgcolor = colors['plot'],
            font = dict(color = colors['text']),
            geo = dict(
                showland=True, showocean=True, 
                showcountries=True, 
            )

        )
    }


# In[ ]:


def create_sentiment_weightage(sentiment_df, unique_sentiment_search_terms, sentiment_term = None):
    
    if sentiment_term is None:
        sentiment_term = [unique_sentiment_search_terms[0]]
    
    sentiment_df['search_term'] = sentiment_df.apply (lambda row: row['sentiment_id'].split('_', 1)[0], axis=1)
    
    dff = sentiment_df[sentiment_df['search_term'].isin(sentiment_term)]
  
    labels = ['Positive', 'Neutral', 'Negative']
    colors_sentiment = ["#00ff00", "#ffff00", "ff0000"]
    
    values = []
    for sentiment in labels:
        count = dff[dff['sentiment']==sentiment]['sentiment'].count()
        values.append(count)
        
    sentiment_title = [i.title() for i in sentiment_term]
    sentiment_title_join = ", ".join(sentiment_title)
    
    return {
        "data": [go.Pie(labels=labels, values=values, hole=.5, marker_colors=colors_sentiment)],
        "layout": go.Layout(
            title= str("Sentiment Weightage for "+ sentiment_title_join),

            showlegend=True,
            legend=go.layout.Legend(
                orientation ="h"
            ),
                  
            plot_bgcolor = colors['plot'],
            paper_bgcolor = colors['plot'],
            font = dict(color = colors['text'])
        )
    }    


# In[ ]:


def create_interaction_graph(graph_df, unique_graph_search_terms, graph_term = None):
    
    if graph_term is None:
        graph_term = [unique_graph_search_terms[0]]
    
    graph_df['search_term'] = graph_df.apply (lambda row: row['graph_id'].split('_', 1)[0], axis=1)
    
    dff = graph_df[graph_df['search_term'].isin(graph_term)]
    
    graph_title = [i.title() for i in graph_term]
    graph_title_join = ", ".join(graph_title)
        
    G = fn.create_network_graph(dff)
    
    edge_trace = go.Scatter(
        x=[],
        y=[],
        mode='lines'
    )
        
    for edge in G.edges():
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
        
    node_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        colorscale='RdBu',
        reversescale=True,
        color=[],
        size=15,
        colorbar=dict(
            thickness=10,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line=dict(width=0))
    )
    
    for node in G.nodes():
        x, y = G.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color']+=tuple([len(adjacencies[1])])
        node_info = str(adjacencies[0]) +' # of connections: '+str(len(adjacencies[1]))
        node_trace['text']+=tuple([node_info])
        
    return {
        "data": [edge_trace, node_trace],
        "layout": go.Layout(
            title= str("Interaction Network for "+ graph_title_join),                 
            plot_bgcolor = colors['plot'],
            paper_bgcolor = colors['plot'],
            showlegend=False,
            font = dict(color = colors['text']),
            annotations=[ dict(
                    text="No. of connections",
                    showarrow=False,
                    xref="paper", yref="paper") ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
    } 


# In[ ]:


def create_page_rank_table(graph_df, unique_graph_search_terms, graph_term = None):

    graph_df = graph_data_on_load

    if graph_term is None:
        graph_term = [unique_graph_search_terms[0]]

    graph_df['search_term'] = graph_df.apply(lambda row: row['graph_id'].split('_', 1)[0], axis=1)

    dff = graph_df[graph_df['search_term'].isin(graph_term)]

    graph_title = [i.title() for i in graph_term]
    graph_title_join = ", ".join(graph_title)

    G = fn.create_network_graph(dff)

    users = fn.return_top_n_users_page_rank(G, 15)

    return {
            "data": [go.Table(
                header=dict(
                        values=['Top Users'],
                        line_color=colors['plot'],
                        font = dict(color = colors['text'], size=20), 
                        align='center',
                        height=50
                        ),
                cells=dict(
                    values=[list(users['Top User Ranking'])],
                    line_color=colors['plot'],

                    font = dict(color = colors['text'], size=15), 
                    align='center',
                    height=50
                
                ))

            ],
            "layout": go.Layout(
                title= str("Top User Ranking for "+ graph_title_join),
                plot_bgcolor = colors['plot'],
                paper_bgcolor = colors['plot'],
                font = dict(color = colors['text']),
  
                
            )
        }    


# In[ ]:


def create_top_words_chart(word_df, unique_word_search_terms, word_term = None):
    
    if word_term is None:
        word_term = [unique_word_search_terms[0]]
    
    word_df['search_term'] = word_df.apply (lambda row: row['word_id'].split('_', 1)[0], axis=1)
    
    dff = word_df[word_df['search_term'].isin(word_term)]
    
    words_frequent = fn.return_word_frequency(dff['text'])
    labels, values = zip(*words_frequent)
    
    labels = [i.title() for i in labels]
    labels = list(labels)
    labels.reverse()
    
    values = list(values)
    values.reverse()
    
    word_title = [i.title() for i in word_term]
    word_title_join = ", ".join(word_title)
    
    return {
        "data": [go.Bar(x=values, y=labels, orientation='h', marker=dict(color='orchid'))],
        "layout": go.Layout(
            title= str("Most Frequent Words for "+ word_title_join),
                             
            plot_bgcolor = colors['plot'],
            paper_bgcolor = colors['plot'],
            font = dict(color = colors['text'])
        )
    }    


# In[ ]:


def create_top_hashtags_chart(hashtag_df, unique_hashtag_search_terms, hashtag_term = None):
    
    if hashtag_term is None:
        hashtag_term = [unique_word_search_terms[0]]
    
    hashtag_df['search_term'] = hashtag_df.apply (lambda row: row['hashtag_id'].split('_', 1)[0], axis=1)
    
    dff = hashtag_df[hashtag_df['search_term'].isin(hashtag_term)]
    
    hashtags_frequent = fn.return_frequent_hashtags(dff['hashtags'])
    labels, values = zip(*hashtags_frequent)
    
    hashtag_title = [i.title() for i in hashtag_term]
    hashtag_title_join = ", ".join(hashtag_title)
    
    return {
        "data": [go.Bar(x=labels, y=values, marker=dict(color='seagreen'))],
        "layout": go.Layout(
            title= str("Most Popular Hashtags for "+ hashtag_title_join),
                             
            plot_bgcolor = colors['plot'],
            paper_bgcolor = colors['plot'],
            font = dict(color = colors['text'])
        )
    }   


# In[ ]:


def create_top_mentioned_users_chart(graph_df, unique_graph_search_terms, graph_term = None):
    
    if graph_term is None:
        graph_term = [unique_graph_search_terms[0]]
    
    graph_df['search_term'] = graph_df.apply (lambda row: row['graph_id'].split('_', 1)[0], axis=1)
    
    dff = graph_df[graph_df['search_term'].isin(graph_term)]
    
    users_frequent = fn.return_frequent_users(dff['user_mentions_screen_name'])
    labels, values = zip(*users_frequent)
    
    graph_title = [i.title() for i in graph_term]
    graph_title_join = ", ".join(graph_title)
    
    return {
        "data": [go.Bar(x=labels, y=values, marker=dict(color='coral'))],
        "layout": go.Layout(
            title= str("Most Mentioned Users for "+ graph_title_join),
                             
            plot_bgcolor = colors['plot'],
            paper_bgcolor = colors['plot'],
            font = dict(color = colors['text'])
        )
    }


# In[ ]:


def create_top_source_chart(hashtag_df, unique_hashtag_search_terms, hashtag_term = None):
    
    if hashtag_term is None:
        hashtag_term = [unique_word_search_terms[0]]
    
    hashtag_df['search_term'] = hashtag_df.apply (lambda row: row['hashtag_id'].split('_', 1)[0], axis=1)
    
    dff = hashtag_df[hashtag_df['search_term'].isin(hashtag_term)]
    
    hashtags_frequent = fn.return_frequent_source(dff['source'])
    labels, values = zip(*hashtags_frequent)
    
    hashtag_title = [i.title() for i in hashtag_term]
    hashtag_title_join = ", ".join(hashtag_title)
    
    return {
        "data": [go.Pie(labels=labels, values=values)],
        "layout": go.Layout(
            title= str("Tweet Sources for "+ hashtag_title_join),
                             
            plot_bgcolor = colors['plot'],
            paper_bgcolor = colors['plot'],
            font = dict(color = colors['text'])
        )
    }   


# ### App Initialization

# In[ ]:


app_name = "Twitter Analysis"
app = dash.Dash(app_name)
application = app.server


# In[ ]:

app.layout = html.Div(
    style={"backgroundColor": colors["main_background"]},
    children=[
        ##Header
        html.Div([
            html.Header(
                html.H1(
                    "Twitter Analyzer",
                    style={
                        "padding": "1.5rem",
                        "align-items": "center",
                        "color": colors["text"],
                        "textAlign": "center",
                    },
                )
            )],className="row",
        ),
                
        ##Tabs
        html.Div([
            dcc.Tabs(
                id="tabs",
            
                children=[


                    ##Tab 1     
                    dcc.Tab(
                        label="Analysis",
                        style = tab_style,
                        selected_style = tab_selected_style,
                        children=[
                         html.Div([
                              html.Div([
                                  html.Br(),
                               html.Div([
                                    html.Label(
                                        "Terms:",
                                        style={
                                            "background-color": colors["background"],
                                            "color": colors["text"],
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="analysis_terms_picker",
                                        options=[
                                            {
                                                "label": id.title(),
                                                "value": id,
                                            }
                                            for id in unique_hashtag_search_terms
                                        ],
                                        clearable=False,
                                        multi=True,
                                        style={"width": "250px"},
                                        value=unique_hashtag_search_terms[0]
    
                                    ),
                                    ],style={ "display": "inline-block","padding-left": "0.5rem", 
                                             "background-color": colors["background"],"color": colors["text"]},
                                ),
                                  
                              ]),
                              html.Div([
                                  html.Br(),
                                html.Div([
                                  dcc.Graph(
                                        id="hashtag",
                                        figure=create_top_hashtags_chart(hashtag_data_on_load, 
                                                                          unique_hashtag_search_terms,
                                                                          [unique_hashtag_search_terms[0]]),
                                        style ={
                                            "padding": "0.5rem",
                                            
                                            "height": "50vh",
                                        },
                                    ),      
                                ],style={"display": "inline-block", 'width': '50%'}),
                                html.Div([
                                    dcc.Graph(
                                        id="source",
                                        figure=create_top_source_chart(hashtag_data_on_load, 
                                                                          unique_hashtag_search_terms,
                                                                          [unique_hashtag_search_terms[0]]),
                                        style ={
                                            "padding": "0.5rem",
                                            "height": "50vh",
                                        },
                                    )
                                    ],style={"display": "inline-block", 'width': '50%'},
                                ), 
                              ]),
                            
                              html.Div([
                                  html.Br(),
                                html.Div([
                                      dcc.Graph(
                                        id="words",
                                        figure=create_top_words_chart(word_data_on_load, 
                                                                    unique_word_search_terms, 
                                                                    [unique_word_search_terms[0]]),
                                        style ={
                                            "padding": "0.5rem",
                                            
                                            "height": "50vh",
                                        },
                                    )
                                    ],style={"display": "inline-block", 'width': '50%'},
                                ), 
                                    
                            
                                html.Div([
                                    dcc.Graph(
                                        id="mentioned_users",
                                        figure=create_top_mentioned_users_chart(graph_data_on_load, 
                                                                          unique_graph_search_terms,
                                                                          [unique_graph_search_terms[0]]),
                                        style ={
                                            "padding": "0.5rem",
                                            "height": "50vh",
                                        },
                                    )
                                    ],style={"display": "inline-block", 'width': '50%'},
                                ), ])
                         ])
            
                    ]),

                    ##Tab 2     
                    dcc.Tab(
                        label="Tweet Sentiment",
                        style = tab_style,
                        selected_style = tab_selected_style,
                        children=[
                        
                          html.Div([
                             html.Br(),
                               html.Div([
                                    html.Label(
                                        "Terms:",
                                        style={
                                            "background-color": colors["background"],
                                            "color": colors["text"],
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="sentiment_terms_picker",
                                        options=[
                                            {
                                                "label": id.title(),
                                                "value": id,
                                            }
                                            for id in unique_sentiment_search_terms
                                        ],
                                        clearable=False,
                                        multi=True,
                                        style={"width": "250px"},
                                        value=unique_sentiment_search_terms[0]
    
                                    ),
                                    ],style={ "display": "inline-block","padding-left": "0.5rem", 
                                             "background-color": colors["background"],"color": colors["text"]},
                                ),
                              
                            html.Div([
                                html.Br(),
                                html.Div([
                                    dcc.Graph(
                                        id="sentiment_map",
                                        figure=create_sentiment_map(sentiment_data_on_load, 
                                                                    unique_sentiment_search_terms, 
                                                                    [unique_sentiment_search_terms[0]]),
                                        style ={
                                            "padding": "0.5rem",
                                            
                                            "height": "100vh",
                                        },
                                    )
                                    ],style={"display": "inline-block", 'width': '60%'},
                                ), 
                                html.Div([
                                    dcc.Graph(
                                        id="sentiment_weightage",
                                        figure=create_sentiment_weightage(sentiment_data_on_load, 
                                                                          unique_sentiment_search_terms,
                                                                          [unique_sentiment_search_terms[0]]),
                                        style ={
                                            "padding": "0.5rem",
                                            "height": "100vh",
                                        },
                                    )
                                    ],style={"display": "inline-block", 'width': '40%'},
                                ), 
                            ])     
                         ]),
            
                    ]),
                            
                    ##Tab 3     
                    dcc.Tab(
                        label="Twitter Graph",
                        style = tab_style,
                        selected_style = tab_selected_style,
                        children=[
                        
                 html.Div([
                             html.Br(),
                               html.Div([
                                    html.Label(
                                        "Terms:",
                                        style={
                                            "background-color": colors["background"],
                                            "color": colors["text"],
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="graph_terms_picker",
                                        options=[
                                            {
                                                "label": id.title(),
                                                "value": id,
                                            }
                                            for id in unique_graph_search_terms
                                        ],
                                        clearable=False,
                                        multi=True,
                                        style={"width": "250px"},
                                        value=unique_graph_search_terms[0]
    
                                    ),
                                    ],style={ "display": "inline-block","padding-left": "0.5rem", 
                                             "background-color": colors["background"],"color": colors["text"]},
                                ),
                              
                            html.Div([
                                html.Br(),
                                html.Div([
                                    dcc.Graph(
                                        id="interaction_map",
                                        figure=create_interaction_graph(graph_data_on_load, 
                                                                        unique_graph_search_terms,
                                                                       [unique_graph_search_terms[0]]),
                                        style ={
                                            "padding": "0.5rem",
                                            "height": "100vh",
                                        },
                                    )
                                    ],style={"display": "inline-block", 'width': '60%'},
                                ), 
                                html.Div([
                                dcc.Graph(
                                        id="user_rank_table",
                                        figure=create_page_rank_table(graph_data_on_load, 
                                                                      unique_graph_search_terms,
                                                                     [unique_graph_search_terms[0]]),
                                        style ={
                                            "padding": "0.5rem",
                                            "height": "100vh",
                                        },
                                    )
                                    ],style={"display": "inline-block", 'width': '40%'},
                                ),             

                            ])     
                         ]),
            
                    ]),
        
 
                ],   style ={
#                     'height': '44px'
                }),
            ]),
        ])

# In[ ]:


@app.callback(Output('sentiment_map', 'figure'),
              [Input('sentiment_terms_picker', 'value')])
def update_sentiment_map(sentiment_term):

    figure = create_sentiment_map(sentiment_data_on_load, unique_sentiment_search_terms, sentiment_term)
        
    return figure


# In[ ]:


@app.callback(Output('sentiment_weightage', 'figure'),
              [Input('sentiment_terms_picker', 'value')])
def update_sentiment_weightage(sentiment_term):
    
    figure = create_sentiment_weightage(sentiment_data_on_load, unique_sentiment_search_terms, sentiment_term)
    
    return figure


# In[ ]:


@app.callback(Output('interaction_map', 'figure'),
              [Input('graph_terms_picker', 'value')])
def update_interaction_map(graph_term):

    figure = create_interaction_graph(graph_data_on_load, unique_graph_search_terms, graph_term)
    
    return figure


# In[ ]:


@app.callback(Output('user_rank_table', 'figure'),
              [Input('graph_terms_picker', 'value')])
def update_user_rank_table(graph_term):
   
    figure = create_page_rank_table(graph_data_on_load, unique_graph_search_terms, graph_term)
    
    return figure


# In[ ]:


@app.callback(Output('hashtag', 'figure'),
              [Input('analysis_terms_picker', 'value')])
def update_hashtags(analysis_term):
   
    figure = create_top_hashtags_chart(hashtag_data_on_load, unique_hashtag_search_terms, analysis_term)
    
    return figure


# In[ ]:


@app.callback(Output('source', 'figure'),
              [Input('analysis_terms_picker', 'value')])
def update_source(analysis_term):
   
    figure = create_top_source_chart(hashtag_data_on_load, unique_hashtag_search_terms, analysis_term)
    
    return figure


# In[ ]:


@app.callback(Output('words', 'figure'),
              [Input('analysis_terms_picker', 'value')])
def update_words(analysis_term):
   
    figure = create_top_words_chart(word_data_on_load, unique_word_search_terms, analysis_term)
    
    return figure


# In[ ]:


@app.callback(Output('mentioned_users', 'figure'),
              [Input('analysis_terms_picker', 'value')])
def update_mentioned_users(analysis_term):
   
    figure = create_top_mentioned_users_chart(graph_data_on_load, unique_graph_search_terms, analysis_term)
    
    return figure


# ### Render App

# In[ ]:


if __name__ == '__main__':
    application.run(debug=True, port=8080)


# In[ ]:





# In[ ]:





# In[ ]:




