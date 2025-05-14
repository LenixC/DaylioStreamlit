import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
import datetime
from utils import add_title
from sklearn.datasets import make_spd_matrix

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


if 'categories' in st.session_state:
    categories = st.session_state.categories
    base_activities = [value for sublist in categories.values() for value in sublist]
else:
    st.session_state.categories = categories


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

def handle_categories(category):
    try:
        input = re.split(r': |, ', category)
        key = input[0]
        values = input[1:]
        if key in st.session_state.categories:
            st.write("AH")
            st.session_state.categories[key].extend(values)
            st.success(f"{', '.join(values)} added to {key}!")
        else:
            st.session_state.categories[key] = values
            st.success(f"Category {key} created with activities {', '.join(values)}")
    except:
        st.error("Something went wrong.")


def gen_data():
    num_days = 365
    covariance_matrix = make_spd_matrix(len(base_activities))

    data = np.random.multivariate_normal(mean=np.zeros(len(base_activities)),
                                         cov=covariance_matrix,
                                         size=num_days)

    data = (data > 0.75).astype(int)

    df = pd.DataFrame(data, columns=base_activities)
    start_date = datetime.datetime.now() - datetime.timedelta(days=num_days-1)
    df['full_date'] = pd.date_range(start=start_date,
                                    periods=num_days,
                                    freq='D')
    df['full_date'] = pd.to_datetime(df['full_date'])
    df['mood'] = np.random.choice(mood_ordering, size=num_days)
    df = df[['full_date'] + ['mood'] + [col for col in df.columns if col != 'full_date' and col != 'mood']]
    df = df.set_index('full_date')
    df['weekday'] = df.index.strftime('%A')
    df_moods = pd.get_dummies(df['mood'])
    df = df.join(df_moods)
    
    st.session_state.df_encoded = df

#add_title()
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

upload_col, gen_col = st.columns(2)
with upload_col:
    st.markdown("##### Upload your Daylio Data")
    uploaded_file = st.file_uploader("", type=["csv"])
with gen_col:
    st.markdown("##### Or generate some dummy data.")
    gen_data_button = st.button("Generate Data")
    if gen_data_button:
        gen_data()
    st.warning("Generated data does not have human behavior, so some pages won't be very interesting.")

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

        if st.button('Yes', disabled='imputed' in st.session_state):
            df_encoded = df_encoded.resample('D').agg(mode_with_ties)
            df_encoded[base_activities + ['mood']] = df_encoded[base_activities + ['mood']].apply(lambda x: x.fillna(safe_mode(x)))
            df_moods = pd.get_dummies(df_encoded['mood'])
            df_encoded = df_encoded.drop(columns=mood_ordering).join(df_moods)
            st.success("We've filled in your missing values.")

            st.session_state.df_encoded = df_encoded
            st.session_state.imputed = True

        st.write(df_encoded)
    except:
        st.write("Hmm... that didn't work.")


with st.expander('Customize Categories'):
    st.markdown('''
                Please list your additional activities in the form of:

                *Category: actvity_1, activity_2, ...*

                Only add information already present in your data.
                ''')
    with st.form('category_form'):
        category_input = st.text_input(label='Category and new activity')
        category_submitted = st.form_submit_button("Submit")
        if category_submitted:
            handle_categories(category_input)
    category_clean = st.button("Clear all customizations")
    if category_clean:
        st.session_state.categories = categories
