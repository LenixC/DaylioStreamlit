import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from mlxtend.frequent_patterns import apriori
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


if 'categories' in st.session_state:
    categories = st.session_state.categories
    base_activities = [value for sublist in categories.values() for value in sublist]


add_title()
st.markdown('''
# Frequent Patterns
Here, we analyze your activities to find the most common relationships through frequent pattern analysis. Support serves as a measure indicating how frequently these patterns occur in your data—higher numbers indicate more prevalent patterns.
''')


if 'df_encoded' in st.session_state:
    df_encoded = st.session_state.df_encoded

    items = df_encoded.filter(base_activities)

    frequent_itemsets = apriori(items, min_support=0.3, use_colnames=True)
    frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(list)
    sorted_freq_items = frequent_itemsets.sort_values('support', ascending=False)
    sorted_freq_items['length'] = sorted_freq_items['itemsets'].apply(lambda x: len(x))
    two_plus_itemsets = sorted_freq_items[(sorted_freq_items['length'] >= 2) & (frequent_itemsets['support'] >= .5)].sort_values(by=['support'], ascending=False)
    two_plus_itemsets['itemsets'] = two_plus_itemsets['itemsets'].apply(', '.join)

    if len(two_plus_itemsets) == 0:
        st.markdown('#### No frequent patterns detected.')
    else:
        n_patterns = st.slider('Top n patterns', 1, len(two_plus_itemsets), 10)

        fig = px.bar(two_plus_itemsets.head(n_patterns)[::-1],
                    x='support',
                    y='itemsets',
                    orientation='h')
        fig.update_layout(showlegend=False,
                        height=800)

        st.plotly_chart(fig, use_container_width=True)
        st.write(frequent_itemsets.sort_values(by='support', ascending=False).set_index('support'))

else:
    st.error("Try uploading something in the Upload Data page.")
