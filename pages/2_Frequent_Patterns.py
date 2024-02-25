import streamlit as st
import pandas as pd
import plotly.express as px
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules


if 'df' in st.session_state:
    df_encoded = st.session_state.df_encoded

    items = df_encoded.drop(columns=['full_date', 'date_exp', 
                                     'weekday', 'time', 'mood'])

    frequent_itemsets = apriori(items, min_support=0.3, use_colnames=True)
    frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(list)
    st.write(frequent_itemsets)
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
