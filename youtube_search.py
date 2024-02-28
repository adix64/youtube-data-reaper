import googleapiclient.discovery

class VideoItem:
    def __init__(self, video_title, view_count, like_count, comment_count, duration, upload_date, channel_title, subscriber_count, channel_view_count, video_count, lv_ratio, vs_ratio, view_ratio, description, tags_string, thumbnail_url, video_link):
        self.video_title = video_title
        self.view_count = view_count
        self.like_count = like_count
        self.comment_count = comment_count
        self.duration = duration
        self.upload_date = upload_date  # Added upload_date
        self.channel_title = channel_title
        self.subscriber_count = subscriber_count
        self.channel_view_count = channel_view_count
        self.video_count = video_count
        self.lv_ratio = lv_ratio
        self.vs_ratio = vs_ratio
        self.view_ratio = view_ratio
        self.description = description
        self.tags_string = tags_string
        self.thumbnail_url = thumbnail_url
        self.video_link = video_link

# Function to execute YouTube search and update the table
def youtube_search(search_query, order_option):
    with open('PASTE_YOUR_API_KEY_HERE.txt', 'r') as file: api_key = ''.join(file.read().split())
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    
    request = youtube.search().list(part="snippet", maxResults=50, q=search_query, type="video", order=order_option)
    response = request.execute()
    video_ids = [item['id']['videoId'] for item in response['items']]
    video_details_request = youtube.videos().list(part="snippet,statistics,contentDetails", id=",".join(video_ids))
    video_details_response = video_details_request.execute()
    video_items = []
    for item in video_details_response['items']:
        video_id = item['id']
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        thumbnail_url = item['snippet']['thumbnails']['high']['url']
        tags = item['snippet'].get('tags', [])
        tags_string = ', '.join(tags)
        
        video_stats = youtube.videos().list(part="statistics", id=video_id).execute()['items'][0]['statistics']
        channel_id = item['snippet']['channelId']
        channel_stats = youtube.channels().list(part="statistics", id=channel_id).execute()['items'][0]['statistics']

        comment_count = int(video_stats.get('commentCount', 0))
        view_count = int(video_stats.get('viewCount', 0))
        like_count = int(video_stats.get('likeCount', 0))
        subscriber_count = int(channel_stats.get('subscriberCount', 0))
        channel_view_count = int(channel_stats.get('viewCount', 0))
        video_count = int(channel_stats.get('videoCount', 0))
        
        lv_ratio = like_count / view_count if view_count else -1
        vs_ratio = view_count / subscriber_count if subscriber_count else -1
        view_ratio = view_count / channel_view_count if channel_view_count else -1
        
        duration = item['contentDetails']['duration']
        upload_date = item['snippet']['publishedAt']  # Extracting upload date

        video_item = VideoItem(
            video_title=item['snippet']['title'],
            view_count=view_count,
            like_count=like_count,
            comment_count=comment_count,
            duration=duration,
            upload_date=upload_date,  # Including upload date in the VideoItem instantiation
            channel_title=item['snippet']['channelTitle'],
            subscriber_count=subscriber_count,
            channel_view_count=channel_view_count,
            video_count=video_count,
            lv_ratio=lv_ratio,
            vs_ratio=vs_ratio,
            view_ratio=view_ratio,
            description=item['snippet']['description'],
            tags_string=tags_string,
            thumbnail_url=thumbnail_url,
            video_link=video_link
        )
        video_items.append(video_item)

    return video_items
