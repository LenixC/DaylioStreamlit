import streamlit as st
import pandas as pd
import plotly.express as px
from utils import add_title

st.set_page_config(layout="wide")

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
weekday_ordering = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


if 'categories' in st.session_state:
    categories = st.session_state.categories
    base_activities = [value for sublist in categories.values() for value in sublist]


add_title()
st.markdown('''
    # Activities Over Time 
    This page shows some core features of your mental health 
    and allows you to explore activities on a week by week basis.
    ''')

def add_date_slider(fig):
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )


def plot_moods(category, df_encoded, is_percent):
    df_week_group = df_encoded.copy().drop(columns=['date_exp', 'weekday', 'time', 'mood'])
    df_weekly = df_week_group.resample('W-Mon').sum()
    title = "Count of Occurrence per Week"
    value = "Count"

    if is_percent:
        df_weekly = df_weekly/7
        title = "Percent of Occurences per Week"
        value = "Percent"

    fig = px.line(df_weekly, x=df_weekly.index, 
                  y=activity_selections,
                  title=title,
                  labels={'full_date': 'Week of ',
                          'value': value,
                          'variable': 'Activity'})
    add_date_slider(fig)

    if is_percent:
        fig.update_yaxes(range=[0, 1.1])

    st.plotly_chart(fig, use_container_width=True)


def plot_day_of_week(category, activities, is_percent):
    day_of_week_df = df_encoded.groupby('weekday')[category].sum()
    day_of_week_df = day_of_week_df.reindex(weekday_ordering)
    title = "Count by Weekday"
    value = "Count"
    if is_percent:
        day_of_week_df = day_of_week_df/7
        title = "Percent Occurrence on Weekday"
        value = "Percent"

    fig = px.bar(day_of_week_df, 
                x=activities,
                y=day_of_week_df.index,
                barmode='group',
                title=title,
                labels={'full_date': 'Week of ',
                          'value': value,
                          'variable': 'Activity'})
    fig.update_layout(yaxis_title=None,
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    if is_percent:
        fig.update_xaxes(range=[0, 1.1])
    
    return fig


def plot_overall_counts(df_encoded, category):
    overall_counts_df = None
    if category == 'Moods':
        overall_counts_df = df_encoded[mood_ordering].sum().sort_values(ascending=True)
    elif category == 'All':
        overall_counts_df = df_encoded[base_activities + mood_ordering].sum().sort_values(ascending=True)

    else:
        overall_counts_df = df_encoded[categories[category]].sum().sort_values(ascending=True)
    fig = px.bar(overall_counts_df,
                    x=overall_counts_df,
                    y=overall_counts_df.index,
                    title="Overall Counts in " + category,
                    labels={'x': 'Total Count', 
                            'index': 'Activity'})
    return fig


def plot_heatmap(df_encoded, category, is_percent):
    df_week_group = df_encoded.copy().drop(columns=['date_exp', 'weekday', 'time', 'mood'])
    df_weekly = df_week_group.resample('W-Mon').sum()
    if category == 'Moods':
        df_weekly = df_weekly[mood_ordering]
    elif category == 'All':
        df_weekly = df_weekly[mood_ordering + base_activities]
    else: 
        df_weekly = df_weekly[categories[category]]
    st.write(df_weekly.describe())
    df_weekly = df_weekly.transpose()
    
    if is_percent:
        df_weekly = (df_weekly/7).applymap(lambda x: f'{x: .2g}')

    fig = px.imshow(df_weekly,
                    text_auto=True)
    fig.update_layout(xaxis=dict(title='Week of'))
    fig.update_coloraxes(showscale=False)
    return fig


if 'df_encoded' in st.session_state:
    try:
        df_encoded = st.session_state.df_encoded
        category_selection = st.selectbox(
            'Select a Category',
            ['Moods'] + list(categories.keys()) + ['All']
        )

        if category_selection == 'Moods':
            is_overall = st.toggle('Overall Moods', value=True)
            if is_overall:
                fig = px.line(df_encoded, x=df_encoded.index, y='mood',
                            labels={'mood': 'Mood',
                                    'full_date': 'Date'})
                fig.update_yaxes(categoryorder='array', categoryarray=mood_ordering,
                                range=[-0.5, 5.0])
                add_date_slider(fig)
                st.plotly_chart(fig, use_container_width=True)
            else:
                activity_selections = st.multiselect(
                    'Select Moods',
                    mood_ordering,
                )
                is_percent = st.checkbox('Percentage?')
                if activity_selections:
                    plot_moods(mood_ordering, df_encoded, is_percent)
                    fig= plot_day_of_week(mood_ordering, activity_selections, is_percent)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(fig, use_container_width=True)
                    fig = plot_overall_counts(df_encoded, 'Moods')
                    with col2:
                        st.plotly_chart(fig, use_container_width=True)
                    fig = plot_heatmap(df_encoded, category_selection, is_percent)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = plot_overall_counts(df_encoded, 'Moods')
                    st.plotly_chart(fig, use_container_width=True)
                    fig = plot_heatmap(df_encoded, category_selection, is_percent)
                    st.plotly_chart(fig, use_container_width=True)
        elif category_selection == 'All':
            activity_selections = st.multiselect(
                'Select Activities',
                mood_ordering + base_activities,
            )
            is_percent = st.checkbox('Percentage?')
            if activity_selections:
                plot_moods(mood_ordering + base_activities, df_encoded, is_percent)
                plot_day_of_week(mood_ordering + base_activities, activity_selections, is_percent)
                plot_overall_counts(df_encoded, category_selection)
                col1, col2 = st.columns(2)
                fig = plot_day_of_week(mood_ordering + base_activities, activity_selections, is_percent)
                with col1:
                    st.plotly_chart(fig, use_container_width=True)
                fig = plot_overall_counts(df_encoded, category_selection)
                with col2:
                    st.plotly_chart(fig, use_container_width=True)
                fig = plot_heatmap(df_encoded, category_selection, is_percent)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = plot_overall_counts(df_encoded, category_selection)
                st.plotly_chart(fig, use_container_width=True)
                fig = plot_heatmap(df_encoded, category_selection, is_percent)
                st.plotly_chart(fig, use_container_width=True)
        else:
            activity_selections = st.multiselect(
                'Select Activities',
                categories[category_selection],
            )
            is_percent = st.checkbox('Percentage?')
            if activity_selections:
                plot_moods(categories[category_selection], df_encoded, is_percent)
                col1, col2 = st.columns(2)
                fig = plot_day_of_week(categories[category_selection], activity_selections, is_percent)
                with col1:
                    st.plotly_chart(fig, use_container_width=True)
                fig = plot_overall_counts(df_encoded, category_selection)
                with col2:
                    st.plotly_chart(fig, use_container_width=True)
                fig = plot_heatmap(df_encoded, category_selection, is_percent)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = plot_overall_counts(df_encoded, category_selection,)
                st.plotly_chart(fig, use_container_width=True)
                fig = plot_heatmap(df_encoded, category_selection, is_percent)
                st.plotly_chart(fig, use_container_width=True)
    except:
        st.error(f"An activity in {category_selection} is not present in your data.")
else:
    st.error("Try uploading something in the Upload Data page.")
