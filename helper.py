from urlextract import URLExtract
import pandas as pd
import streamlit as st
from wordcloud import WordCloud
from collections import Counter
import emoji

extractor = URLExtract()  # Create once globally

@st.cache_data
def fetch_stats(selected_user, df):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]
    #fetch messages
    num_messages=df.shape[0]
    #fetch words
    words = ' '.join(df['message']).split()
    #fetch number of media messages
    num_media_messages = df['message'].str.contains('<Media omitted>').sum()
    # fetch number of links
    links=[]

    for message in df['message']:
        links.extend(extractor.find_urls(message))

    return num_messages, len(words),num_media_messages,len(links)

@st.cache_data
def most_busy_users(df):
    df_filtered = df[df['user']!='group_notification']
    x = df_filtered['user'].value_counts().head()
    new_df = round((df_filtered['user'].value_counts()/df_filtered.shape[0])*100,2).reset_index().rename(columns={'index':'name','user':'percent'})
    return x, new_df

def create_wordcloud(selected_user, df):
    f=open('stop_hinglish.txt','r')
    stop_words=f.read().split()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    temp= df[df['user'] != 'group_notification']
    temp=temp[~temp['message'].str.contains('<Media omitted>', na=False)]

    def remove_stop_words(message):
        y=[]
        for word in message.lower().split():
            if word not in stop_words and not any(char.isdigit() for char in word):
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    
    temp['message'] = temp['message'].apply(remove_stop_words)
    wordcloud = wc.generate(temp['message'].str.cat(sep=" "))
    return wordcloud

def most_common_words(selected_user, df):
    # This function can be implemented to return the most common words
    f=open('stop_hinglish.txt','r')
    stop_words=f.read().split()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    temp= df[df['user'] != 'group_notification']
    temp=temp[~temp['message'].str.contains('<Media omitted>', na=False)]

    words=[]

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words and not any(char.isdigit() for char in word):
                words.append(word)

    most_common_df=pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))), columns=['emoji', 'count'])
    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df.copy()
    df['year_month'] = df['date'].dt.to_period('M')
    timeline = df.groupby('year_month')['message'].count().reset_index()
    timeline.columns = ['time', 'message']
    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap
 