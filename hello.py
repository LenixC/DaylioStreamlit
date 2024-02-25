import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

base_activities = ['happy', 'excited', 'grateful', 'relaxed', 
                   'content', 'tired', 'unsure', 'bored', 'anxious', 
                   'angry', 'stressed', 'sad', 'desperate',
                   'sleep early', 'good sleep', 'medium sleep', 'bad sleep',
                   'exercise', 'eat healthy', 'drink water', 'walk', 
                   'movies & tv', 'reading', 'gaming', 'sport', 'relax',
                   'fast food', 'homemade', 'restaurant', 'delivery', 'no meat', 'no sweets', 'no soda',
                   'family', 'friends', 'date', 'party',
                   'meditation', 'kindness', 'listen','donate', 
                   'give gift',
                   'start early', 'make list', 'focus', 'take a break',
                   'shopping', 'cleaning', 'cooking', 'laundry']
categories = {"Emotions": ['happy', 'excited', 'grateful',
                           'relaxed', 'content', 'tired',
                           'unsure', 'bored', 'anxious', 'angry',
                           'stressed', 'sad', 'desperate'],
              "Sleep": ['sleep early', 'good sleep', 'medium sleep', 'bad sleep'],
              "Health": ['exercise', 'eat healthy', 'drink water', 'walk'],
              "Hobbies": ['movies & tv', 'reading', 'gaming', 'sport', 'relax'],
              "Food": ['fast food', 'homemade', 'restaurant', 
                       'delivery', 'no meat', 'no sweets', 'no soda'],
              "Social": ['family', 'friends', 'date', 'party'],
              "Better Me": ['meditation', 'kindness', 'listen',
                            'donate', 'give gift'],
              "Productivity": ['start early', 'make list', 'focus', 'take a break'],
              "Chores": ['shopping', 'cleaning', 'cooking', 'laundry']
}
mood_ordering = ['awful', 'bad', 'meh', 'good', 'rad']


uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
@st.cache_data
def load_and_prep_data(file):
    df = pd.read_csv(file)
    df['activities'] = df['activities'].str.split('|').apply(lambda x: [e.strip() for e in x])
    df = df.drop(columns=['note_title', 'note'])
    df['mood'] = pd.Categorical(df['mood'], categories=mood_ordering, ordered=True)

    df_activities = pd.get_dummies(df['activities'].explode(), 
                                   columns=base_activities).groupby(level=0).sum()
    df_activities = df_activities.rename(columns=lambda x: x.strip())
    for col in base_activities:
        if col not in df_activities.columns:
            df_activities[col] = 0

    df_moods = pd.get_dummies(df['mood'])

    df = df.rename(columns={'date': 'date_exp'})
    df_joined = (df.drop('activities', axis=1).join(df_activities))
    df_joined = (df_joined).join(df_moods)

    st.session_state.df = df
    st.session_state.df_encoded = df_joined

    return df, df_joined

if uploaded_file or 'df' in st.session_state:
    df = None
    df_encoded = None
    if uploaded_file:
        df, df_encoded = load_and_prep_data(uploaded_file)
        st.session_state.df = df
        st.session_state.df_encoded = df_encoded
    elif 'df' in st.session_state:
        df = st.session_state.df
        df_encoded = st.session_state.df_encoded
    st.write(df)



    st.sidebar.success("Testing.")

