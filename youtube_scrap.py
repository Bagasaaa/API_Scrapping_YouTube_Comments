import pandas as pd
import re
from googleapiclient.discovery import build

api_key = 'AIzaSyCjfZSyUAolMsXvnNLCVpCc13ZtFBl1j3Q'

def video_comments(video_id):
    # empty list for storing reply
    replies = []

    # creating youtube resource object
    youtube = build('youtube', 'v3', developerKey=api_key)

    # retrieve youtube video results
    video_response = youtube.commentThreads().list(part='snippet,replies', videoId=video_id).execute()

    # iterate video response
    while video_response:

        # extracting required info
        # from each result object
        for item in video_response['items']:

            # extracting comments
            published = item['snippet']['topLevelComment']['snippet']['publishedAt']
            netizen = item['snippet']['topLevelComment']['snippet']['authorDisplayName']

            # Extracting comments
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            likeCount = item['snippet']['topLevelComment']['snippet']['likeCount']

            replies.append([published, netizen, comment, likeCount])

            # counting number reply of comment
            replyCount = item['snippet']['totalReplyCount']

            # if reply is there
            if replyCount>0:
                # iterate through all reply
                for reply in item['replies']['comments']:

                    # Extract reply
                    published = reply['snippet']['publishedAt']
                    netizen = reply['snippet']['authorDisplayName']
                    repl = reply['snippet']['textDisplay']
                    likeCount = reply['snippet']['likeCount']

                    replies.append([published, netizen, repl, likeCount])

        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
            part = 'snippet,replies',
            pageToken = video_response['nextPageToken'],
            videoId = video_id
            ).execute()
        else:
            break
    return replies

def get_video_metadata(video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    video_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    # extract video title and channel name
    video_title = video_response['items'][0]['snippet']['title']
    channel_name = video_response['items'][0]['snippet']['channelTitle']

    return video_title, channel_name

def get_video_data(video_url):
    # ambil id video dari url menggunakan regex
    video_id = re.findall(r'(?<=v=)[\w-]{11}', video_url)[0]

    comments = video_comments(video_id)
    title, channel = get_video_metadata(video_id)
    return comments, title, channel

def get_video_comments_df(video_url):
    # ambil id video dari url menggunakan regex
    video_id = re.findall(r'(?<=v=)[\w-]{11}', video_url)[0]

    # Ambil metadata video
    title, channel = get_video_metadata(video_id)

    # Ambil komentar video
    comments = video_comments(video_id)

    # Buat DataFrame
    df = pd.DataFrame(comments, columns=['time', 'netizen', 'comment', 'like_count'])

    # Tambahkan kolom metadata
    df['channel'] = channel
    df['title'] = title

    # extract tanggal and jam
    df['date'] = df['time'].str.split('T').str[0]
    df['date'] = pd.to_datetime(df['date'])
    df['hour'] = df['time'].str.split('T').str[1].str[:-1]
    df['hour'] = pd.to_datetime(df['hour'], format='%H:%M:%S').dt.strftime('%H:%M:%S')

    # drop the original 'time' column
    df.drop('time', axis=1, inplace=True)

    # Pilih kolom yang diperlukan
    df = df[['channel', 'title', 'date', 'hour', 'netizen', 'comment', 'like_count']]

    return df