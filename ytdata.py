from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timezone
import isodate
import time

load_dotenv()  # Load environment variables from .env
api_key = os.getenv("YT_API_KEY")

# Initialize YouTube client
youtube = build('youtube', 'v3', developerKey=api_key)

# NHL team YouTube handles
teams = {
    'Carolina Hurricanes': '@CarolinaHurricanes',
    'Dallas Stars': '@DallasStars',
    'Edmonton Oilers': '@EdmontonOilers',
    'Florida Panthers': '@floridapanthersvideo',
    'Toronto Maple Leafs': '@TorontoMapleLeafs',
    'Vegas Golden Knights': '@vegasgoldenknights',
    'Washington Capitals': '@Capitals',
    'Winnipeg Jets': '@NHLJets'
}

# Date filter: May 5–12, 2025
START_DATE = datetime(2025, 5, 5, tzinfo=timezone.utc)
END_DATE = datetime(2025, 5, 12, tzinfo=timezone.utc)

all_videos = []

for team, handle in teams.items():
    print(f"🔍 Scraping {team} ({handle})...")

    # Step 1: Search for the channel
    search_resp = youtube.search().list(
        part="snippet",
        q=handle,
        type="channel",
        maxResults=1
    ).execute()

    if not search_resp['items']:
        print(f"❌ No search result for {team}")
        continue

    channel = search_resp['items'][0]
    channel_id = channel['snippet']['channelId']
    print(f"✅ Found channel ID: {channel_id}")

    # Step 2: Get uploads playlist + subscriber count
    channel_resp = youtube.channels().list(
        part='contentDetails,statistics',
        id=channel_id
    ).execute()

    if not channel_resp['items']:
        print(f"❌ Channel details not found for {team}")
        continue

    uploads_id = channel_resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    subscriber_count = int(channel_resp['items'][0]['statistics'].get('subscriberCount', 0))

    # Step 3: Get video IDs within date range
    video_ids = []
    next_page = None

    while True:
        playlist_resp = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page
        ).execute()

        for item in playlist_resp['items']:
            published_at = datetime.fromisoformat(
                item['contentDetails']['videoPublishedAt'].replace("Z", "+00:00"))
            if START_DATE <= published_at <= END_DATE:
                video_ids.append(item['contentDetails']['videoId'])

        next_page = playlist_resp.get('nextPageToken')
        if not next_page:
            break

    print(f"📺 {len(video_ids)} videos found in date range.")

    # Step 4: Get video details
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        vid_resp = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(batch)
        ).execute()

        for v in vid_resp['items']:
            snippet = v['snippet']
            stats = v.get('statistics', {})
            content = v.get('contentDetails', {})
            duration = content.get('duration')
            duration_min = isodate.parse_duration(duration).total_seconds() / 60 if duration else None

            all_videos.append({
                'team': team,
                'video_id': v['id'],
                'title': snippet.get('title'),
                'published': snippet.get('publishedAt'),
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'duration_minutes': round(duration_min, 2) if duration_min else None,
                'subscribers': subscriber_count
            })

        time.sleep(0.2)

# Save to CSV
df = pd.DataFrame(all_videos)
df.to_csv("nhldata.csv", index=False)
print("✅ Data saved to nhldata.csv")