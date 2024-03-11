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
# Frequent Patterns
Here, we analyze your activities to find the most common relationships through frequent pattern analysis. Support serves as a measure indicating how frequently these patterns occur in your data—higher numbers indicate more prevalent patterns.
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


if 'df' in st.session_state:
    df_encoded = st.session_state.df_encoded

    items = df_encoded.drop(columns=['full_date', 'date_exp', 
                                     'weekday', 'time', 'mood'])

    frequent_itemsets = apriori(items, min_support=0.3, use_colnames=True)
    frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(list)
    st.write(frequent_itemsets.sort_values(by='support', ascending=False).set_index('support'))
    sorted_freq_items = frequent_itemsets.sort_values('support', ascending=False)
    sorted_freq_items['length'] = sorted_freq_items['itemsets'].apply(lambda x: len(x))
    two_plus_itemsets = sorted_freq_items[(sorted_freq_items['length'] >= 2) & (frequent_itemsets['support'] >= .5)].sort_values(by=['support'], ascending=False)
    two_plus_itemsets['itemsets'] = two_plus_itemsets['itemsets'].apply(', '.join)

    n_patterns = st.slider('Top n patterns', 1, len(two_plus_itemsets), 10)

    fig = px.bar(two_plus_itemsets.head(n_patterns)[::-1],
                 x='support',
                 y='itemsets',
                 orientation='h')

    st.plotly_chart(fig, use_container_width=True)

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
                 labels={'value': 'Correlation',
                         'index': 'Activity'})
    fig.update_layout(showlegend=False,
                      height=800)
    st.plotly_chart(fig, use_container_width=True)

    st.write(phi_results)

else:
    st.error("Try uploading something in the Upload Data page.")
