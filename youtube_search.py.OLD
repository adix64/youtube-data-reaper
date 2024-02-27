import googleapiclient.discovery
# Function to execute YouTube search and update the table
def youtube_search(search_query, order_option):
    with open('PASTE_YOUR_API_KEY_HERE.txt', 'r') as file: api_key = ''.join(file.read().split())
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    
    request = youtube.search().list(part="snippet", maxResults=50, q=search_query, type="video", order=order_option)
    response = request.execute()
    # Collect all video IDs into a list, to make a videos().list() call to get details for all vids
    video_ids = [item['id']['videoId'] for item in response['items']]
    video_details_request = youtube.videos().list(part="snippet,statistics,contentDetails", id=",".join(video_ids))
    video_details_response = video_details_request.execute()
    video_items = []
    for item in video_details_response['items']:
        video_id = item['id']
        video_title = item['snippet']['title']
        channel_id = item['snippet']['channelId']
        duration = item['contentDetails']['duration']
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        thumbnailURL = item['snippet']['thumbnails']['medium']['url'] # could be either 'default', 'medium', 'high', 'standard' or 'maxres'
        tags = item['snippet']['tags'] if 'tags' in item['snippet'] else []
        channel_title = item['snippet']['channelTitle']
        tags_string = ', '.join(tags)
        
        video_stats = youtube.videos().list(part="statistics", id=video_id).execute()['items'][0]['statistics']
        channel_stats = youtube.channels().list(part="statistics", id=channel_id).execute()['items'][0]['statistics']

        commentCount = int(video_stats.get('commentCount', 0))
        viewCount = int(video_stats.get('viewCount', 0))
        likeCount = int(video_stats.get('likeCount', 0))
        subscriberCount = int(channel_stats.get('subscriberCount', 0))
        channelViewCount = int(channel_stats.get('viewCount', 0))
        videoCount = int(channel_stats.get('videoCount', 0))
        
        lvRatio = likeCount / viewCount if (viewCount > 0) else -1
        vsRatio = viewCount / subscriberCount if (subscriberCount > 0) else -1
        viewRatio = viewCount / channelViewCount if (channelViewCount > 0) else -1
        # Append a tuple with all relevant information
        video_items.append((video_title, viewCount, likeCount, commentCount, 
                            channel_title, subscriberCount, channelViewCount, videoCount,
                            lvRatio, vsRatio, viewRatio,
                            item['snippet']['description'], tags_string, thumbnailURL, video_link))

    # Sort the list by likeCount in descending order
    # video_items.sort(key=lambda x: x[2], reverse=True)
    return video_items
    
    