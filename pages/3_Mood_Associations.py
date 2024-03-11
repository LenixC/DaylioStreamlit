import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from scipy.stats import chi2_contingency
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

add_title()
st.markdown('''
# Mood Associations
This page employs the phi coefficient to identify which activities have the most significant impact on your mood. Larger numbers indicate that an activity is commonly associated with that mood, while negative numbers suggest that the activity is often associated with the absence of that mood.
''')


def phi_coefficient(col1, col2, df):
    try:
        contingency_table = pd.crosstab(df[col1], df[col2])
        a = contingency_table.iloc[0, 0]
        b = contingency_table.iloc[0, 1]
        c = contingency_table.iloc[1, 0]
        d = contingency_table.iloc[1, 1]
        phi = (a*d - b*c) / np.sqrt((a + b) * (c + d) * (a + c) * (b + d))
        return phi
    except:
        return 0

def phi_correlation_sets(set1, set2, df):
    phi_results = pd.DataFrame(index=set1, columns=set2)
    for col1 in set1:
        for col2 in set2:
            phi_results.at[col1, col2] = phi_coefficient(col1, col2, df)
    return phi_results.transpose()


if 'df_encoded' in st.session_state:
    df_encoded = st.session_state.df_encoded

    col_names = [df_encoded[col].name for col in base_activities]

    negative_mode = ['awful', 'bad']
    positive_mode = ['good', 'rad']

    df_joined_moods = df_encoded.copy()
    df_joined_moods['negative moods'] = df_joined_moods['awful'] + df_joined_moods['bad']
    df_joined_moods['positive moods'] = df_joined_moods['good'] + df_joined_moods['rad']
    corr_joined = df_joined_moods[base_activities 
        + ['negative moods', 'meh', 'positive moods']].corr(method='spearman')[['negative moods', 'meh', 'positive moods']]

    correlations = df_encoded[base_activities + mood_ordering].corr(method='spearman')[mood_ordering]


    mood_select = st.selectbox(
        'Select a Mood',
        ('negative moods', 'meh', 'positive moods', 'awful', 'bad', 'meh', 'good', 'rad'),
    )

    df_joined_moods[base_activities] = df_joined_moods[base_activities].fillna(0)

    set1 = []
    set2 = [col for col in base_activities if df_encoded[col].nunique() == 2]

    if mood_select in ['negative moods', 'meh', 'positive moods']:
        set1 = ['negative moods', 'meh', 'positive moods']
    else:
        set1 = ['awful', 'bad', 'meh', 'good', 'rad']
    phi_results = phi_correlation_sets(set1, set2, df_joined_moods.dropna())

    if st.checkbox('Sorted?'):
        phi_results = phi_results.sort_values(by=mood_select)

    fig = px.bar(phi_results.dropna(),
                 x=phi_results[mood_select],
                 y=phi_results.index,
                 orientation='h',
                 labels={'x': 'Strength',
                         'y': 'Activity'})
    fig.update_layout(showlegend=False,
                      height=800)
    st.plotly_chart(fig, use_container_width=True)

    st.write(phi_results)

else:
    st.error("Try uploading something in the Upload Data page.")
