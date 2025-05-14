# Daylio Inspector

Daylio Inspector is your personal companion to better understanding yourself
and your moods. It utilizes the popular 
[Daylio mood tracking app](https://daylio.net/)
as a collection point for analyzing your mental health. 

## Upload Data
When first opening the application, you are brought to the home screen which
allows you to upload a .csv file from the Daylio app. If you are just curious,
you can instead generate synthetic data, however, the data doesn't very
interesting statistical properties. Additionally, you can impute your missing
data with your most common moods, so if you forget for a few days, the app can
simply guess that you were having your default mood. Finally, you may add 
custom categories, a Daylio feature that allows you to define your own
moods and experience as you wish.

## Activities Over Time
This page shows the quality of your moods over the span of your dataset, as well as
allowing you to map activities and see how certain activities align with other
activities or moods. In addition to this, you get a breakdown of how commonly
you experience different moods, and on what days you feel them.

## Frequent Patterns
This section indicates frequent patterns identified in your daily moods and
activities. For instance, you may find that "sports, energized, happy" is a
frequent pattern, meaning that you do it quite a bit, and that they tend to
all clump together. This is done using the frequent itemset analysis known as
the Apriori Algorithm.

## Mood Associations
This page utilizes the $\phi$ coefficient to identify which activities have the 
most significant impact on your different moods. For instance, you may find that
movies are postiviely associated with good moods, but cleaning is negatively 
associated with good moods. 

## Stack
This application is made using python, pandas, mlxtend, streamlit, and plotly.
