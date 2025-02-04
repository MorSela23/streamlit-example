# -*- coding: utf-8 -*-
"""Data_Visualization_Project (1).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vuJs0OdPiCHDg7h9dWUkQxBulC8j0FBn
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re

# ---------------------------------------------------------------------------------------------------

netflix_data = pd.read_csv('n_movies.csv')
netflix_titles = pd.read_csv('netflix_titles.csv')
merged_df = pd.merge(netflix_data, netflix_titles, on='title', how='inner')
df = pd.merge(netflix_data,netflix_titles[['title','director','country','date_added','type']],on='title', how='left')
df = df.drop('certificate', axis=1)

# ------------------------------------------------------------------------------------------------------------
def bar_chart(df):
    genre_counts = df['genre'].str.split(', ', expand=True).stack().value_counts().reset_index()
    genre_counts.columns = ['index', 'value']
    genre_counts = genre_counts.sort_values('value')
    genre_counts['index'] = pd.Categorical(genre_counts['index'], categories=genre_counts['index'])
    
    # Calculate average duration for each genre
    genre_avg_duration = df['genre'].str.split(', ', expand=True).stack().reset_index(level=0).rename(columns={0: 'genre'})
    genre_avg_duration['duration'] = df['duration'].str.split(' ').str[0]
    genre_avg_duration['duration'] = pd.to_numeric(genre_avg_duration['duration'], errors='coerce')
    genre_avg_duration = genre_avg_duration.groupby('genre')['duration'].mean().reset_index()
    
    # Merge average duration into genre_counts DataFrame
    genre_counts = pd.merge(genre_counts, genre_avg_duration, left_on='index', right_on='genre')
    genre_counts = genre_counts.drop('genre', axis=1)
    
    genre_chart = go.Figure(data=[go.Bar(x=genre_counts['value'], y=genre_counts['index'], orientation='h', marker=dict(color='#E64A19'),
                                        text=genre_counts['duration'].round(2), textposition='auto',
                                        hovertemplate='Duration: %{text}')])
    
    genre_chart.update_layout(
                              xaxis=dict(title="Count"),
                              yaxis=dict(title="Genre"),
                              bargap=0.2)
    
    
    # Streamlit app
    # st.title("Genre Distribution Bar Chart")
    st.plotly_chart(genre_chart)

# ------------------------------------------------------------------------------------------------------------

def heatmap(df):
    # Generate the graph
    genre_counts = df['genre'].str.split(', ').explode().value_counts().reset_index()
    
    # Create a dropdown select box for genres
    genre_dropdown = st.selectbox(
        'Select Genre',
        genre_counts,
        index=0,
        key='genre-dropdown'
    )
    
    # Define the container for the graph
    heatmap_output = st.empty()
    
    # Define the callback function to update the graph
    @st.cache
    def update_heatmap(genre):
        # Filter the data based on the selected genre
        netflix_date_genre = df[df['genre'].str.contains(genre, na=False)][['date_added']].dropna()
        netflix_date_genre['year'] = netflix_date_genre['date_added'].apply(lambda x: x.split(', ')[-1])
        netflix_date_genre['month'] = netflix_date_genre['date_added'].apply(lambda x: x.lstrip().split(' ')[0])
    
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][::-1]
        df_genre = netflix_date_genre.groupby('year')['month'].value_counts().unstack().fillna(0)[month_order].T
    
        # Generate the updated graph using Plotly Express
        heatmap_fig = px.imshow(df_genre.values,
                        labels=dict(x="Year", y="Month", color="Count"),
                        x=df_genre.columns,
                        y=df_genre.index,
                        color_continuous_scale='Reds')
    
        heatmap_fig.update_layout(
            title=f'Netflix Contents Update for Genre: {genre}',
            font_family='Ariel',
            height=500,
            width=800
        )
    
        return heatmap_fig
    
    # Call the callback function and update the graph
    heatmap_fig = update_heatmap(genre_dropdown)
    
    # Display the graph
    heatmap_output.plotly_chart(heatmap_fig)

# ---------------------------------------------------------------------------------------------------------------------
def choropleth_map(df):
    # Calculate average rating/popularity score per country
    avg_rating = df.groupby('country')['rating'].mean().reset_index()
    
    # Create the choropleth map
    choropleth_map = px.choropleth(avg_rating, locations='country', locationmode='country names',
                                   color='rating', color_continuous_scale=['#F1DDCF', '#C81914'],
                                   hover_name='country', hover_data=['rating'],
                                   projection='natural earth')
    
    # Customize marker and layout
    choropleth_map.update_traces(marker=dict(line=dict(color='rgb(200,200,200)', width=1)))
    choropleth_map.update_geos(showframe=False, showcoastlines=False)
    
    # Display the choropleth map using Streamlit
    st.plotly_chart(choropleth_map)
# -------------------------------------------------------------------------------------------------------------------

def line_chart(df):
    # Drop 'NA' values from the 'type' column
    df = df.dropna(subset=['type'])
    
    # Remove null values from the 'rating' column
    df = df[~df['rating'].isnull()]
    
    # Convert 'year' column to string
    df['year'] = df['year'].astype(str)
    
    # Filter out values from the 'year' column that do not fit the 4-digit string representation
    df['year'] = df['year'].str.extract(r'(\d{4})').astype(int)
    
    # Convert 'year' column to numeric
    df['year'] = pd.to_numeric(df['year'])
    
    
    # Group by year and type, and calculate the average rating
    grouped_df = df.groupby(['year', 'type'])['rating'].mean().reset_index()
    
    # Create the line chart
    line_chart = go.Figure()
    
    line_chart.add_trace(go.Scatter(
        x=grouped_df.loc[grouped_df['type'] == 'TV Show', 'year'],
        y=grouped_df.loc[grouped_df['type'] == 'TV Show', 'rating'],
        mode='lines+markers',
        name='TV Show',
        marker=dict(color="#DD2C00"),
        line=dict(color="#DD2C00"),
        hovertemplate="<b>Year:</b> %{x}<br><b>Average Rating:</b> %{y}<br>",
        showlegend=True
    ))
    
    line_chart.add_trace(go.Scatter(
        x=grouped_df.loc[grouped_df['type'] == 'Movie', 'year'],
        y=grouped_df.loc[grouped_df['type'] == 'Movie', 'rating'],
        mode='lines+markers',
        name='Movie',
        marker=dict(color="#EDB781"),
        line=dict(color="#EDB781"),
        hovertemplate="<b>Year:</b> %{x}<br><b>Average Rating:</b> %{y}<br>",
        showlegend=True
    ))
    
    line_chart.update_layout(
        
        xaxis=dict(title="Year", range=[df['year'].min(), df['year'].max()], rangeslider=dict(visible=True)),
        yaxis=dict(title="Average Rating"),
        hovermode="closest",
        legend=dict(
            traceorder='grouped',
            itemsizing="constant"
        )
    )
    
    line_chart.add_shape(
        type="line",
        x0=grouped_df.loc[grouped_df['type'] == 'TV Show', 'year'].tolist(),
        y0=grouped_df.loc[grouped_df['type'] == 'TV Show', 'rating'].tolist(),
        x1=grouped_df.loc[grouped_df['type'] == 'TV Show', 'year'].tolist()[1:],
        y1=grouped_df.loc[grouped_df['type'] == 'TV Show', 'rating'].tolist()[1:],
        line=dict(color="#DD2C00")
    )
    
    line_chart.add_shape(
        type="line",
        x0=grouped_df.loc[grouped_df['type'] == 'Movie', 'year'].tolist(),
        y0=grouped_df.loc[grouped_df['type'] == 'Movie', 'rating'].tolist(),
        x1=grouped_df.loc[grouped_df['type'] == 'Movie', 'year'].tolist()[1:],
        y1=grouped_df.loc[grouped_df['type'] == 'Movie', 'rating'].tolist()[1:],
        line=dict(color="#FF8A65")
    )
    
    
    # Streamlit app
    st.plotly_chart(line_chart)


# -------------------------------------------------------------------------------------------------------------------------

st.set_page_config(layout="wide")
# Set the title of the dashboard
# st.title("Netflix")

col1, col2, col3 = st.columns(3)
with col2:
    title_photo = "netflix_logo.jpg"
    st.image(title_photo, use_column_width=False, width=400)
    st.subheader("Analyzing Most Popular Content")
    
col4, col5 = st.columns(2, gap="large")
with col4:
    st.header("Genre Distribution")
    bar_chart(df)
with col5:
    st.header("Average Rating per Country")
    choropleth_map(df)

col6, col7 = st.columns(2, gap="large")
with col6:
    st.header("Netflix Contents Update per Genre")
    heatmap(df)
with col7:
    st.header("Average Rating Over Years")
    line_chart(df)

