import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import add_title

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


def mode_with_ties(series):
    mode_result = series.mode()
    return mode_result[0] if not mode_result.empty else None


def safe_mode(series):
    mode_counts = series.value_counts()
    if len(mode_counts) > 1:
        return mode_counts.index[1]  # Second most common value
    else:
        return series.mode().iloc[0]


@st.cache_data
def load_and_prep_data(file):
    df = pd.read_csv(file, parse_dates=['full_date'], index_col=['full_date'])
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

    st.session_state.df_encoded = df_joined

    return df, df_joined

add_title()
st.markdown('''
# Howdy!

This app is here to support you in understanding your Daylio Mood Tracking information in a relaxed and therapeutic way.

To begin, follow these steps:

1. Open your Daylio app.
2. Go to More > Export Entries > CSV (table).
3. Download your data.
4. Upload the data here.
5. Explore the tabs on the left-hand side.

None of your data is stored on our end. 
''')

uploaded_file = st.file_uploader("Upload Your Daylio Data", type=["csv"])

if uploaded_file or 'df_encoded' in st.session_state:
    try:
        df = None
        df_encoded = None
        if uploaded_file:
            df, df_encoded = load_and_prep_data(uploaded_file)
            st.session_state.df_encoded = df_encoded
        elif 'df_encoded' in st.session_state:
            df_encoded = st.session_state.df_encoded
        st.success("Upload successful. Check out the Activities Over Time page!")
        st.write('Would you like us to fill in the missing data using the most common value?')
        if st.checkbox('Yes'):
            df_encoded = df_encoded.resample('D').agg(mode_with_ties)
            df_encoded[base_activities + mood_ordering + ['mood']] = df_encoded[base_activities + mood_ordering + ['mood']].apply(lambda x: x.fillna(safe_mode(x)))
            st.session_state.df_encoded = df_encoded
        st.write(df_encoded)
    except:
        st.write("Hmm... that didn't work.")
