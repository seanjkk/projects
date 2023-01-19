import pandas as pd
import tweepy
import config

# Connecting to the Twitter API using Tweepy's Paginator method to retrieve a csv file of users' Tweet data
def twitter_to_csv(twitter_ids):
    client = tweepy.Client(
        bearer_token=config.bearer_token,
        consumer_key=config.consumer_key,
        consumer_secret=config.consumer_secret,
        access_token=config.access_key,
        access_token_secret=config.access_secret,
        wait_on_rate_limit=True
        )
    
    df_final = pd.DataFrame()

    for twitter_id in twitter_ids:
        paginator =  tweepy.Paginator(
            client.get_users_tweets,
            id=twitter_id,
            start_time='2022-01-01T00:00:00Z',
            end_time='2023-01-01T00:00:00Z',
            exclude=['retweets', 'replies'],
            tweet_fields=['author_id', 'created_at', 'lang', 'public_metrics'], 
            expansions=['author_id', 'attachments.media_keys'],
            user_fields=['username', 'public_metrics'],
            media_fields=['media_key'],
            max_results=100,
            limit=2
        )

        df = pd.DataFrame()

        for page in paginator:
            df = df.append(page.data)
        
        df = df.join(pd.json_normalize(df['public_metrics'])).drop('public_metrics', axis='columns')

        df_final = df_final.append(df)
    
    df_final.to_csv("data/tweets.csv")

# Twitter IDs for Ronaldo, Neymar and Mbappe
twitter_ids = [155659213, 158487331, 1725137533]

twitter_to_csv(twitter_ids)